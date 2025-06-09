"""
File operations endpoints for the FastAPI web service.

This module handles file upload, download, backup, and restore operations.
"""

import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Response

from appearance.api.models import (
    FileUploadResponse,
    BackupCreateResponse,
    RestoreRequest,
    MessageResponse
)
from appearance.api.session import (
    SessionStorage, 
    get_session_storage, 
    SessionData,
    validate_profiles_format
)
from appearance.service import list_characters

router = APIRouter(prefix="/api/sessions/{session_id}", tags=["files"])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def get_session_or_404(session_id: str, storage: SessionStorage) -> SessionData:
    """Get session or raise 404 error."""
    session = await storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/upload", response_model=FileUploadResponse)
async def upload_profiles_file(
    session_id: str,
    file: UploadFile = File(..., description="profiles.dat file to upload"),
    storage: SessionStorage = Depends(get_session_storage)
):
    """Upload a profiles.dat file to the session."""
    session = await get_session_or_404(session_id, storage)
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    if not file.filename or not file.filename.lower().endswith('.dat'):
        raise HTTPException(
            status_code=400,
            detail="File must have .dat extension"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate profiles.dat format
        if not validate_profiles_format(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid profiles.dat format. File must be a valid Mount & Blade profiles file."
            )
        
        # Create backup of current session data before replacing
        if len(session.profiles_data) > 12:  # Has more than just header
            await storage.add_backup(session_id)
        
        # Update session with new data
        await storage.update_session_data(session_id, content)
        
        # Count characters in uploaded file
        temp_path = session.save_profiles_to_temp()
        try:
            characters = list_characters(profiles_file_path=temp_path)
            char_count = len(characters)
        except Exception:
            char_count = 0
        
        return FileUploadResponse(
            message="File uploaded successfully",
            character_count=char_count,
            file_size=len(content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/download")
async def download_profiles_file(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Download the current profiles.dat file from the session."""
    session = await get_session_or_404(session_id, storage)
    
    try:
        # Return the current profiles data as a downloadable file
        return Response(
            content=session.profiles_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=profiles.dat"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )

@router.post("/backup", response_model=BackupCreateResponse)
async def create_backup(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Create a backup of the current session state."""
    session = await get_session_or_404(session_id, storage)
    
    try:
        # Create backup
        await storage.add_backup(session_id)
        
        backup_id = f"backup_{len(session.backups)}"
        
        return BackupCreateResponse(
            backup_id=backup_id,
            created_at=session.last_accessed,
            message="Backup created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )

@router.post("/restore", response_model=MessageResponse)
async def restore_from_backup(
    session_id: str,
    request: RestoreRequest,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Restore session from a backup."""
    session = await get_session_or_404(session_id, storage)
    
    try:
        if not session.backups:
            raise HTTPException(
                status_code=404,
                detail="No backups available for this session"
            )
        
        # Determine which backup to restore
        backup_index = -1  # Default to latest
        if request.backup_id:
            try:
                # Extract backup number from backup_id (e.g., "backup_3" -> 2 for 0-based index)
                backup_num = int(request.backup_id.split('_')[1])
                backup_index = backup_num - 1
            except (ValueError, IndexError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid backup_id format"
                )
        
        # Restore from backup
        success = await storage.restore_from_backup(session_id, backup_index)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Backup not found"
            )
        
        return MessageResponse(message="Session restored from backup successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore from backup: {str(e)}"
        )

@router.get("/backups")
async def list_backups(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """List all available backups for the session."""
    session = await get_session_or_404(session_id, storage)
    
    backups = []
    for i, backup_data in enumerate(session.backups):
        backups.append({
            "backup_id": f"backup_{i + 1}",
            "size": len(backup_data),
            "created_at": session.created_at,  # Simplified - in real implementation you'd track individual timestamps
            "index": i
        })
    
    return {
        "session_id": session_id,
        "backup_count": len(backups),
        "backups": backups
    }

@router.delete("/backups/{backup_id}", response_model=MessageResponse)
async def delete_backup(
    session_id: str,
    backup_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Delete a specific backup."""
    session = await get_session_or_404(session_id, storage)
    
    try:
        # Extract backup index from backup_id
        backup_num = int(backup_id.split('_')[1])
        backup_index = backup_num - 1
        
        if backup_index < 0 or backup_index >= len(session.backups):
            raise HTTPException(
                status_code=404,
                detail="Backup not found"
            )
        
        # Remove the backup
        session.backups.pop(backup_index)
        
        return MessageResponse(message="Backup deleted successfully")
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid backup_id format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete backup: {str(e)}"
        )

@router.get("/export")
async def export_characters_json(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    """Export characters as JSON for external use."""
    session = await get_session_or_404(session_id, storage)
    
    try:
        # Save current data to temp file and list characters
        temp_path = session.save_profiles_to_temp()
        characters = list_characters(profiles_file_path=temp_path)
        
        # Convert to exportable format
        export_data = {
            "session_id": session_id,
            "exported_at": session.last_accessed.isoformat(),
            "character_count": len(characters),
            "characters": [
                {
                    "index": idx,
                    "name": char.get('name', ''),
                    "sex": char.get('sex', 0),
                    "skin": char.get('skin', 0),
                    "age": char.get('age', 0),
                    "hairstyle": char.get('hairstyle', 0),
                    "hair_color": char.get('hair_color', 0),
                    "banner": char.get('banner', 0),
                    "face_code": char.get('face_code', '')
                }
                for idx, char in enumerate(characters)
            ]
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export characters: {str(e)}"
        )