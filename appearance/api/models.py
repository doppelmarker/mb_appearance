"""
Pydantic models for the FastAPI web service.

This module contains all request/response models used by the API endpoints.
"""

from datetime import datetime
from typing import Dict, Optional, List, Tuple

from pydantic import BaseModel, Field, validator

from appearance.validators import validate_name

# Configuration constants
MAX_CHARACTERS_PER_GENERATION = 100

# ============================================================================
# Session Models
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request to create a new session, optionally with file upload."""
    pass

class SessionInfo(BaseModel):
    """Session information response."""
    session_id: str
    character_count: int
    created_at: datetime
    last_accessed: datetime
    has_backups: bool

# ============================================================================
# Character Models
# ============================================================================

class CharacterInfo(BaseModel):
    """Character information with all properties."""
    index: int
    name: str
    sex: int  # 0=Male, 1=Female
    skin: int  # 0,16,32,48,64
    age: int
    hairstyle: int
    hair_color: int
    banner: int
    face_code: str  # 64-char hex

class CharacterCreateRequest(BaseModel):
    """Request to create a new character."""
    name: str = Field(..., min_length=1, max_length=28)
    sex: int = Field(..., ge=0, le=1)
    skin: int = Field(0, description="Skin tone: 0,16,32,48,64")
    age: Optional[int] = Field(None, ge=0, le=63)
    hairstyle: Optional[int] = Field(None, ge=0)
    hair_color: Optional[int] = Field(None, ge=0, le=63)
    face_code: Optional[str] = None

    @validator('skin')
    def validate_skin(cls, v):
        if v not in [0, 16, 32, 48, 64]:
            raise ValueError('Skin must be one of: 0, 16, 32, 48, 64')
        return v

    @validator('name')
    def validate_name_chars(cls, v):
        if not validate_name(v):
            raise ValueError('Name contains invalid characters or is too long')
        return v

class CharacterUpdateRequest(BaseModel):
    """Request to update an existing character."""
    name: Optional[str] = Field(None, min_length=1, max_length=28)
    sex: Optional[int] = Field(None, ge=0, le=1)
    skin: Optional[int] = None
    age: Optional[int] = Field(None, ge=0, le=63)
    hairstyle: Optional[int] = Field(None, ge=0)
    hair_color: Optional[int] = Field(None, ge=0, le=63)
    face_code: Optional[str] = None

    @validator('skin')
    def validate_skin(cls, v):
        if v is not None and v not in [0, 16, 32, 48, 64]:
            raise ValueError('Skin must be one of: 0, 16, 32, 48, 64')
        return v

    @validator('name')
    def validate_name_chars(cls, v):
        if v is not None and not validate_name(v):
            raise ValueError('Name contains invalid characters or is too long')
        return v

class GenerateCharactersRequest(BaseModel):
    """Request to generate random characters."""
    count: int = Field(..., ge=1, le=MAX_CHARACTERS_PER_GENERATION)
    sex_filter: Optional[int] = Field(None, ge=0, le=1)
    skin_filter: Optional[int] = None
    age_range: Optional[Tuple[int, int]] = None

    @validator('skin_filter')
    def validate_skin_filter(cls, v):
        if v is not None and v not in [0, 16, 32, 48, 64]:
            raise ValueError('Skin filter must be one of: 0, 16, 32, 48, 64')
        return v

# ============================================================================
# Face Code Models
# ============================================================================

class FaceCodeComponents(BaseModel):
    """Face code component breakdown for 3D morph editing."""
    morph_keys: Dict[str, int] = Field(..., description="43 morph target values")
    hair: int = Field(..., ge=0, description="Hair style index")
    beard: int = Field(..., ge=0, description="Beard style index")
    skin: int = Field(..., description="Skin tone")
    hair_texture: int = Field(..., ge=0, description="Hair texture")
    hair_color: int = Field(..., ge=0, le=63, description="Hair color")
    age: int = Field(..., ge=0, le=63, description="Character age")
    skin_color: int = Field(..., description="Skin color variation")

class FaceCodeEncodeRequest(BaseModel):
    """Request to encode morph components into face code."""
    components: FaceCodeComponents

class FaceCodeDecodeResponse(BaseModel):
    """Response with decoded face code components."""
    face_code: str
    components: FaceCodeComponents

class FaceCodeApplyRequest(BaseModel):
    """Request to apply face code to character."""
    face_code: str

    @validator('face_code')
    def validate_face_code_format(cls, v):
        from appearance.face_code import validate_face_code
        if not validate_face_code(v):
            raise ValueError('Invalid face code format')
        return v

class FaceCodeValidateRequest(BaseModel):
    """Request to validate face code format."""
    face_code: str

class FaceCodeValidateResponse(BaseModel):
    """Response for face code validation."""
    valid: bool
    error: Optional[str] = None

# ============================================================================
# File Operation Models
# ============================================================================

class BackupCreateResponse(BaseModel):
    """Response for backup creation."""
    backup_id: str
    created_at: datetime
    message: str

class RestoreRequest(BaseModel):
    """Request to restore from backup."""
    backup_id: Optional[str] = None  # If None, restore from latest

class FileUploadResponse(BaseModel):
    """Response for file upload."""
    message: str
    character_count: int
    file_size: int

# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_type: str
    field: Optional[str] = None

class ValidationErrorDetail(BaseModel):
    """Detailed validation error."""
    field: str
    message: str
    invalid_value: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Response for validation errors."""
    detail: str = "Validation failed"
    error_type: str = "validation_error"
    errors: List[ValidationErrorDetail]

# ============================================================================
# Utility Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str

class StatisticsResponse(BaseModel):
    """Character statistics response."""
    total_characters: int
    male_count: int
    female_count: int
    skin_distribution: Dict[str, int]
    age_distribution: Dict[str, int]