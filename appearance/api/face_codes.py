"""
Face code operations endpoints for the FastAPI web service.

This module handles face code encoding, decoding, and validation operations.
"""

from fastapi import APIRouter, HTTPException

from appearance.api.models import (
    FaceCodeComponents,
    FaceCodeEncodeRequest,
    FaceCodeDecodeResponse,
    FaceCodeValidateRequest,
    FaceCodeValidateResponse
)
from appearance.face_code import (
    parse_face_code_components,
    generate_face_code,
    validate_face_code,
    format_face_code
)

router = APIRouter(prefix="/api/face-codes", tags=["face-codes"])

@router.get("/{face_code}/decode", response_model=FaceCodeDecodeResponse)
async def decode_face_code(face_code: str):
    """Decode a face code into its component parts for 3D editing."""
    try:
        # Validate face code format first
        if not validate_face_code(face_code):
            raise HTTPException(status_code=400, detail="Invalid face code format")
        
        # Parse components
        components = parse_face_code_components(face_code)
        
        # Convert to our Pydantic model
        face_components = FaceCodeComponents(
            morph_keys=components.get('morph_keys', {}),
            hair=components.get('hair', 0),
            beard=components.get('beard', 0),
            skin=components.get('skin', 0),
            hair_texture=components.get('hair_texture', 0),
            hair_color=components.get('hair_color', 0),
            age=components.get('age', 0),
            skin_color=components.get('skin_color', 0)
        )
        
        return FaceCodeDecodeResponse(
            face_code=format_face_code(face_code),
            components=face_components
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid face code: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode face code: {str(e)}")

@router.post("/encode", response_model=dict)
async def encode_face_code(request: FaceCodeEncodeRequest):
    """Encode morph components back into a face code."""
    try:
        # Convert Pydantic model back to dict for the face code generator
        components_dict = {
            'morph_keys': request.components.morph_keys,
            'hair': request.components.hair,
            'beard': request.components.beard,
            'skin': request.components.skin,
            'hair_texture': request.components.hair_texture,
            'hair_color': request.components.hair_color,
            'age': request.components.age,
            'skin_color': request.components.skin_color
        }
        
        # Generate face code
        face_code = generate_face_code(components_dict)
        
        return {
            "face_code": face_code,
            "formatted_face_code": format_face_code(face_code)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid component values: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encode face code: {str(e)}")

@router.post("/validate", response_model=FaceCodeValidateResponse)
async def validate_face_code_endpoint(request: FaceCodeValidateRequest):
    """Validate if a face code has the correct format."""
    try:
        is_valid = validate_face_code(request.face_code)
        
        if is_valid:
            return FaceCodeValidateResponse(valid=True)
        else:
            return FaceCodeValidateResponse(
                valid=False,
                error="Face code format is invalid. Must be 64 hexadecimal characters."
            )
            
    except Exception as e:
        return FaceCodeValidateResponse(
            valid=False,
            error=f"Validation error: {str(e)}"
        )

@router.get("/{face_code}/format")
async def format_face_code_endpoint(face_code: str, include_prefix: bool = True):
    """Format a face code for display."""
    try:
        if not validate_face_code(face_code):
            raise HTTPException(status_code=400, detail="Invalid face code format")
        
        formatted = format_face_code(face_code, include_prefix=include_prefix)
        
        return {
            "original": face_code,
            "formatted": formatted,
            "include_prefix": include_prefix
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to format face code: {str(e)}")

@router.get("/{face_code}/components-summary")
async def get_face_code_summary(face_code: str):
    """Get a summary of face code components without full morph details."""
    try:
        if not validate_face_code(face_code):
            raise HTTPException(status_code=400, detail="Invalid face code format")
        
        components = parse_face_code_components(face_code)
        
        # Return just the appearance parameters, not all 43 morph values
        summary = {
            "face_code": format_face_code(face_code),
            "appearance": {
                "hair": components.get('hair', 0),
                "beard": components.get('beard', 0),
                "skin": components.get('skin', 0),
                "hair_texture": components.get('hair_texture', 0),
                "hair_color": components.get('hair_color', 0),
                "age": components.get('age', 0),
                "skin_color": components.get('skin_color', 0)
            },
            "morph_count": len(components.get('morph_keys', {}))
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get face code summary: {str(e)}")

@router.post("/convert")
async def convert_face_code_format(request: dict):
    """Convert between different face code formats (with/without 0x prefix)."""
    face_code = request.get('face_code')
    target_format = request.get('format', 'prefixed')  # 'prefixed' or 'plain'
    
    if not face_code:
        raise HTTPException(status_code=400, detail="face_code is required")
    
    try:
        if not validate_face_code(face_code):
            raise HTTPException(status_code=400, detail="Invalid face code format")
        
        if target_format == 'prefixed':
            converted = format_face_code(face_code, include_prefix=True)
        elif target_format == 'plain':
            converted = format_face_code(face_code, include_prefix=False)
        else:
            raise HTTPException(status_code=400, detail="Format must be 'prefixed' or 'plain'")
        
        return {
            "original": face_code,
            "converted": converted,
            "format": target_format
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert face code: {str(e)}")