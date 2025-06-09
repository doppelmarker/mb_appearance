"""
Character management endpoints for the FastAPI web service.

This module handles all character CRUD operations within sessions.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from appearance.api.models import (
    CharacterInfo, 
    CharacterCreateRequest, 
    CharacterUpdateRequest,
    GenerateCharactersRequest,
    MessageResponse
)
from appearance.api.session import SessionStorage, get_session_storage, SessionData
from appearance.service import list_characters, delete_character, generate_n_random_characters
from appearance.face_code import extract_face_code, apply_face_code

router = APIRouter(prefix="/api/sessions/{session_id}/characters", tags=["characters"])

async def get_session_or_404(session_id: str, storage: SessionStorage) -> SessionData:
    """Get session or raise 404 error."""
    session = await storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

def convert_character_to_info(char_data: dict, index: int) -> CharacterInfo:
    """Convert character data dict to CharacterInfo model."""
    return CharacterInfo(
        index=index,
        name=char_data.get('name', ''),
        sex=char_data.get('sex', 0),
        skin=char_data.get('skin', 0),
        age=char_data.get('age', 0),
        hairstyle=char_data.get('hairstyle', 0),
        hair_color=char_data.get('hair_color', 0),
        banner=char_data.get('banner', 0),
        face_code=char_data.get('face_code', '')
    )

@router.get("", response_model=List[CharacterInfo])
async def list_session_characters(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """List all characters in the session."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file and list characters
    temp_path = session.save_profiles_to_temp()
    
    try:
        characters = list_characters(profiles_file_path=temp_path)
        return [
            convert_character_to_info(char, idx) 
            for idx, char in enumerate(characters)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list characters: {str(e)}")

@router.get("/{character_index}", response_model=CharacterInfo)
async def get_character(
    session_id: str,
    character_index: int,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Get a specific character by index."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file and list characters
    temp_path = session.save_profiles_to_temp()
    
    try:
        characters = list_characters(profiles_file_path=temp_path)
        
        if character_index < 0 or character_index >= len(characters):
            raise HTTPException(status_code=404, detail="Character not found")
        
        return convert_character_to_info(characters[character_index], character_index)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get character: {str(e)}")

@router.delete("/{character_index}", response_model=MessageResponse)
async def delete_session_character(
    session_id: str,
    character_index: int,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Delete a character from the session."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file
    temp_path = session.save_profiles_to_temp()
    
    try:
        # Verify character exists first
        characters = list_characters(profiles_file_path=temp_path)
        if character_index < 0 or character_index >= len(characters):
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Create backup before deletion
        await storage.add_backup(session_id)
        
        # Delete character
        success = delete_character(temp_path, index=character_index)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete character")
        
        # Update session data
        session.load_profiles_from_temp()
        
        return MessageResponse(message="Character deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete character: {str(e)}")

@router.post("/generate", response_model=List[CharacterInfo])
async def generate_random_characters(
    session_id: str,
    request: GenerateCharactersRequest,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Generate random characters in the session."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file
    temp_path = session.save_profiles_to_temp()
    
    try:
        # Create backup before generation
        await storage.add_backup(session_id)
        
        # Generate characters
        generate_n_random_characters(
            request.count,
            profiles_file_path=temp_path
        )
        
        # Update session data
        session.load_profiles_from_temp()
        
        # Return the newly generated characters
        characters = list_characters(profiles_file_path=temp_path)
        return [
            convert_character_to_info(char, idx) 
            for idx, char in enumerate(characters[-request.count:])  # Return last N characters
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate characters: {str(e)}")

@router.put("/{character_index}", response_model=CharacterInfo)
async def update_character(
    session_id: str,
    character_index: int,
    request: CharacterUpdateRequest,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Update a character's properties."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file
    temp_path = session.save_profiles_to_temp()
    
    try:
        # Verify character exists
        characters = list_characters(profiles_file_path=temp_path)
        if character_index < 0 or character_index >= len(characters):
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Create backup before modification
        await storage.add_backup(session_id)
        
        # For now, we'll need to implement character updating in the service layer
        # This is a placeholder - in practice, you'd need to add an update_character function
        # to the service module or implement the binary manipulation here
        
        # TODO: Implement character property updates
        # This would involve:
        # 1. Reading the character bytes at the correct offset
        # 2. Updating the specific fields (name, sex, skin, etc.)
        # 3. Writing back to the file
        
        raise HTTPException(
            status_code=501, 
            detail="Character updates not yet implemented - will be added in next iteration"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character: {str(e)}")

@router.get("/{character_index}/face-code")
async def get_character_face_code(
    session_id: str,
    character_index: int,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Get the face code for a specific character."""
    session = await get_session_or_404(session_id, storage)
    
    # Save current data to temp file
    temp_path = session.save_profiles_to_temp()
    
    try:
        characters = list_characters(profiles_file_path=temp_path)
        
        if character_index < 0 or character_index >= len(characters):
            raise HTTPException(status_code=404, detail="Character not found")
        
        face_code = characters[character_index].get('face_code', '')
        
        return {"face_code": face_code}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get face code: {str(e)}")

@router.put("/{character_index}/face-code", response_model=CharacterInfo)
async def apply_face_code_to_character(
    session_id: str,
    character_index: int,
    request: dict,  # Expecting {"face_code": "..."}
    storage: SessionStorage = Depends(get_session_storage)
):
    """Apply a face code to a character."""
    session = await get_session_or_404(session_id, storage)
    
    face_code = request.get('face_code')
    if not face_code:
        raise HTTPException(status_code=400, detail="face_code is required")
    
    # Save current data to temp file
    temp_path = session.save_profiles_to_temp()
    
    try:
        # Verify character exists
        characters = list_characters(profiles_file_path=temp_path)
        if character_index < 0 or character_index >= len(characters):
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Create backup before modification
        await storage.add_backup(session_id)
        
        # TODO: Implement face code application
        # This would involve:
        # 1. Reading the character bytes
        # 2. Applying the face code using apply_face_code function
        # 3. Writing back to the profiles file
        
        raise HTTPException(
            status_code=501,
            detail="Face code application not yet implemented - will be added in next iteration"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply face code: {str(e)}")