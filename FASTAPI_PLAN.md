# FastAPI Implementation Plan for Warband Face Editor

This document outlines the complete FastAPI implementation plan for creating a web API wrapper around the mb-app functionality to support the warband-face-editor project.

## **Project Overview**

The warband-face-editor is a web-based 3D character face customization tool for Mount & Blade Warband. It needs a REST API to:
- Upload/download Mount & Blade profiles.dat files
- List and manipulate characters within those files  
- Decode/encode face codes for 3D visualization
- Apply real-time face modifications
- Support session-based file management

## **Core Requirements Analysis**

Based on the existing mb-app codebase capabilities:

### **Available Functionality**
- ✅ Complete face code parsing/generation (43 morph values + appearance)
- ✅ Character CRUD operations (list, create, delete, modify)
- ✅ Binary file I/O for profiles.dat
- ✅ Cross-platform Mount & Blade directory detection
- ✅ Backup/restore functionality
- ✅ Comprehensive validation functions
- ✅ Random character generation

### **Web API Requirements**
- 🎯 Session-based file management (upload profiles.dat, modify, download)
- 🎯 RESTful character manipulation endpoints
- 🎯 Face code encode/decode for 3D morph integration
- 🎯 Real-time character face modifications
- 🎯 CORS support for browser access
- 🎯 Thread-safe concurrent operations

## **API Endpoint Architecture**

### **1. Session Management**
```
POST   /api/sessions                    # Create session (optionally with file upload)
GET    /api/sessions/{session_id}       # Get session info  
DELETE /api/sessions/{session_id}       # Cleanup session
```

**Purpose**: Manage temporary workspaces for uploaded profiles.dat files

### **2. File Operations**
```
POST   /api/sessions/{session_id}/upload    # Upload profiles.dat to session
GET    /api/sessions/{session_id}/download  # Download modified profiles.dat
POST   /api/sessions/{session_id}/backup    # Create backup of current state
POST   /api/sessions/{session_id}/restore   # Restore from backup
```

**Purpose**: Handle file upload/download and backup/restore operations

### **3. Character Management**
```
GET    /api/sessions/{session_id}/characters           # List all characters
GET    /api/sessions/{session_id}/characters/{index}   # Get specific character
POST   /api/sessions/{session_id}/characters           # Create new character
PUT    /api/sessions/{session_id}/characters/{index}   # Update character properties
DELETE /api/sessions/{session_id}/characters/{index}   # Delete character
POST   /api/sessions/{session_id}/characters/generate  # Generate random characters
```

**Purpose**: Full CRUD operations on characters within a session

### **4. Face Code Operations (Stateless)**
```
GET    /api/face-codes/{face_code}/decode   # Decode face code to 43 morph components
POST   /api/face-codes/encode              # Encode morph components to face code  
POST   /api/face-codes/validate            # Validate face code format
```

**Purpose**: Stateless face code operations for 3D morph integration

### **5. Face Application (Stateful)**
```
PUT    /api/sessions/{session_id}/characters/{index}/face-code   # Apply face code to character
GET    /api/sessions/{session_id}/characters/{index}/face-code   # Get character's face code
```

**Purpose**: Apply face modifications to characters in session

## **Data Models & API Contracts**

### **Core Data Models**

```python
# Session Models
class SessionCreateRequest(BaseModel):
    file: Optional[UploadFile] = None

class SessionInfo(BaseModel):
    session_id: str
    character_count: int
    created_at: datetime
    last_accessed: datetime
    has_backups: bool

# Character Models
class CharacterInfo(BaseModel):
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
    name: str = Field(..., min_length=1, max_length=28)
    sex: int = Field(..., ge=0, le=1)
    skin: int = Field(..., regex="^(0|16|32|48|64)$")
    age: Optional[int] = Field(None, ge=0, le=63)
    hairstyle: Optional[int] = Field(None, ge=0)
    hair_color: Optional[int] = Field(None, ge=0, le=63)
    face_code: Optional[str] = None

class CharacterUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=28)
    sex: Optional[int] = Field(None, ge=0, le=1)
    skin: Optional[int] = None
    age: Optional[int] = Field(None, ge=0, le=63)
    hairstyle: Optional[int] = Field(None, ge=0)
    hair_color: Optional[int] = Field(None, ge=0, le=63)
    face_code: Optional[str] = None

# Face Code Models
class FaceCodeComponents(BaseModel):
    # Morph targets (43 values)
    morph_keys: Dict[str, int] = Field(..., description="43 morph target values")
    
    # Appearance parameters
    hair: int = Field(..., ge=0, description="Hair style index")
    beard: int = Field(..., ge=0, description="Beard style index") 
    skin: int = Field(..., description="Skin tone")
    hair_texture: int = Field(..., ge=0, description="Hair texture")
    hair_color: int = Field(..., ge=0, le=63, description="Hair color")
    age: int = Field(..., ge=0, le=63, description="Character age")
    skin_color: int = Field(..., description="Skin color variation")

class FaceCodeEncodeRequest(BaseModel):
    components: FaceCodeComponents

class FaceCodeDecodeResponse(BaseModel):
    face_code: str
    components: FaceCodeComponents

# Generation Models
class GenerateCharactersRequest(BaseModel):
    count: int = Field(..., ge=1, le=100, description="Number of characters to generate")
    sex_filter: Optional[int] = Field(None, ge=0, le=1, description="Constrain to specific sex")
    skin_filter: Optional[int] = Field(None, description="Constrain to specific skin tone")
    age_range: Optional[Tuple[int, int]] = Field(None, description="Age range constraint")

# Error Models
class ValidationError(BaseModel):
    detail: str
    field: Optional[str] = None
    value: Optional[Any] = None

class FileOperationError(BaseModel):
    detail: str
    operation: str
    file_path: Optional[str] = None

class FaceCodeError(BaseModel):
    detail: str
    face_code: Optional[str] = None
    component: Optional[str] = None
```

## **Implementation Phases**

### **Phase 1: Core FastAPI Setup**
**Timeline: Day 1**

**Tasks:**
- [ ] Create `appearance/web_api.py` with FastAPI app
- [ ] Define all Pydantic models for requests/responses
- [ ] Set up CORS middleware for browser access
- [ ] Add comprehensive error handling with proper HTTP status codes
- [ ] Create basic health check endpoint

**Deliverables:**
- Working FastAPI app with model definitions
- CORS configured for development
- Error handling middleware
- Basic API documentation auto-generated

### **Phase 2: Session Management**
**Timeline: Day 1-2**

**Tasks:**
- [ ] Implement in-memory session storage (thread-safe dict)
- [ ] Add session creation/cleanup endpoints
- [ ] Implement auto-expiry for old sessions (configurable timeout)
- [ ] Thread-safe session access using asyncio locks
- [ ] Session cleanup background task

**Integration Points:**
- No direct mb-app integration (pure session management)

**Deliverables:**
- Session CRUD endpoints working
- Thread-safe session storage
- Auto-cleanup functionality

### **Phase 3: File Operations**
**Timeline: Day 2**

**Tasks:**
- [ ] File upload endpoint with validation
- [ ] File download with proper Content-Disposition headers
- [ ] Backup/restore functionality using existing service functions
- [ ] Session-based file storage in temporary directories
- [ ] File size limits and validation

**Integration Points:**
- `service.backup()` for backup operations
- `service.restore_from_backup()` for restore operations
- `helpers.read_profiles()` and `helpers.write_profiles()` for file I/O
- `validators.validate_file_exists()` for file validation

**Deliverables:**
- File upload/download endpoints
- Backup/restore endpoints
- Proper file handling with cleanup

### **Phase 4: Character CRUD**
**Timeline: Day 2-3**

**Tasks:**
- [ ] Character listing with face code extraction
- [ ] Individual character retrieval
- [ ] Character creation/deletion using existing service functions
- [ ] Character updates with validation
- [ ] Random character generation endpoint

**Integration Points:**
- `service.list_characters()` for character listing
- `service.delete_character()` for character deletion
- `service.generate_n_random_characters()` for generation
- `face_code.extract_face_code()` for face code extraction
- `validators.validate_name()`, `validate_sex()` for validation

**Deliverables:**
- Complete character CRUD API
- Character generation endpoint
- Proper validation and error handling

### **Phase 5: Face Code API**
**Timeline: Day 3**

**Tasks:**
- [ ] Stateless face code decode/encode endpoints
- [ ] Face code validation endpoint
- [ ] Character face code application endpoint
- [ ] Integration with existing face_code.py functions

**Integration Points:**
- `face_code.parse_face_code_components()` for decoding
- `face_code.generate_face_code()` for encoding
- `face_code.validate_face_code()` for validation
- `face_code.apply_face_code()` for character application

**Deliverables:**
- Face code encode/decode endpoints
- Face code application to characters
- Complete morph component access

### **Phase 6: Advanced Features**
**Timeline: Day 4**

**Tasks:**
- [ ] Character search/filtering query parameters
- [ ] Bulk operations (multiple character updates)
- [ ] Export/import endpoints for JSON format
- [ ] Statistics endpoint (character distribution)
- [ ] Enhanced error responses with detailed validation

**Integration Points:**
- Extended use of existing validation functions
- Custom filtering logic built on `service.list_characters()`

**Deliverables:**
- Advanced query capabilities
- Bulk operation support
- JSON export/import
- Statistics and analytics

### **Phase 7: Deployment & Docker**
**Timeline: Day 4-5**

**Tasks:**
- [ ] Create Dockerfile for web service
- [ ] Add docker-compose.yml for easy development
- [ ] Environment configuration for production
- [ ] Health check endpoints
- [ ] Logging configuration
- [ ] Production CORS settings

**Deliverables:**
- Production-ready Docker setup
- Environment configuration
- Health monitoring
- Production deployment guide

## **Technical Implementation Details**

### **Session Storage Strategy**

```python
# Thread-safe in-memory session storage
from asyncio import Lock
from typing import Dict, Optional
import asyncio

class SessionStorage:
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        self._lock = Lock()
    
    async def create_session(self, session_id: str, profiles_data: bytes) -> None:
        async with self._lock:
            self._sessions[session_id] = SessionData(
                profiles_data=profiles_data,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                backups=[]
            )
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.last_accessed = datetime.utcnow()
            return session
```

### **Error Handling Strategy**

```python
# HTTP Status Code Mapping
400 Bad Request: 
    - Validation errors (invalid face codes, character data)
    - Malformed requests (invalid JSON, missing fields)
    - File format errors (not a valid profiles.dat)

404 Not Found:
    - Session not found
    - Character index out of range
    - Backup not found

409 Conflict:
    - Character name already exists
    - Cannot delete last character
    - Session already has data

413 Payload Too Large:
    - Uploaded file exceeds size limit
    - Too many characters requested for generation

422 Unprocessable Entity:
    - Valid JSON but semantic errors
    - Face code format valid but values out of range

500 Internal Server Error:
    - Unexpected file I/O errors
    - Binary data corruption
    - System-level errors
```

### **CORS Configuration**

```python
# Development CORS (permissive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production CORS (restrictive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://warband-face-editor.com"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### **Key Integration Points**

The FastAPI implementation will leverage existing mb-app functionality:

**Character Operations:**
- `service.list_characters()` → `GET /api/sessions/{id}/characters`
- `service.delete_character()` → `DELETE /api/sessions/{id}/characters/{index}`  
- `service.generate_n_random_characters()` → `POST /api/sessions/{id}/characters/generate`

**Face Code Operations:**
- `face_code.parse_face_code_components()` → `GET /api/face-codes/{code}/decode`
- `face_code.generate_face_code()` → `POST /api/face-codes/encode`
- `face_code.apply_face_code()` → `PUT /api/sessions/{id}/characters/{index}/face-code`

**File Operations:**
- `helpers.read_profiles()` → File upload processing
- `helpers.write_profiles()` → File download generation
- `service.backup()` → `POST /api/sessions/{id}/backup`

**Validation:**
- `validators.validate_name()` → Character name validation in Pydantic models
- `validators.validate_sex()` → Sex field validation
- `face_code.validate_face_code()` → Face code format validation

### **Thread Safety Considerations**

1. **Session Storage**: Use asyncio.Lock() for thread-safe session access
2. **File Operations**: Each session gets isolated temporary directory
3. **Character Modifications**: Lock session during character updates
4. **Memory Management**: Implement session cleanup to prevent memory leaks

### **File Upload/Download Handling**

```python
# File Upload
@app.post("/api/sessions/{session_id}/upload")
async def upload_profiles(
    session_id: str,
    file: UploadFile = File(...),
    storage: SessionStorage = Depends(get_session_storage)
):
    # Validate file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    
    # Read and validate profiles.dat format
    content = await file.read()
    if not _validate_profiles_format(content):
        raise HTTPException(400, "Invalid profiles.dat format")
    
    # Store in session
    await storage.update_session(session_id, content)
    
    return {"message": "File uploaded successfully"}

# File Download
@app.get("/api/sessions/{session_id}/download")
async def download_profiles(
    session_id: str,
    storage: SessionStorage = Depends(get_session_storage)
):
    session = await storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    return Response(
        content=session.profiles_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=profiles.dat"}
    )
```

## **Success Criteria**

### **Functional Requirements**
- ✅ Web API exposes all face code functionality
- ✅ Browser can upload/download profiles.dat files  
- ✅ Face codes can be decoded/encoded via REST
- ✅ Characters can be modified through API
- ✅ Ready for Three.js frontend integration

### **Technical Requirements**
- ✅ Thread-safe concurrent access
- ✅ Proper error handling and validation
- ✅ CORS configuration for browser access
- ✅ Session-based file management
- ✅ Auto-cleanup of expired sessions

### **Performance Requirements**
- ✅ Handle multiple concurrent sessions
- ✅ Fast face code encode/decode operations
- ✅ Efficient character listing for large profiles
- ✅ Minimal memory footprint per session

### **Deployment Requirements**
- ✅ Docker deployment ready
- ✅ Environment configuration support
- ✅ Health check endpoints
- ✅ Production logging configuration

## **API Usage Examples**

### **Basic Workflow**

```javascript
// 1. Create session and upload file
const formData = new FormData();
formData.append('file', profilesFile);
const session = await fetch('/api/sessions', {
    method: 'POST',
    body: formData
}).then(r => r.json());

// 2. List characters
const characters = await fetch(`/api/sessions/${session.session_id}/characters`)
    .then(r => r.json());

// 3. Decode a face code for 3D editing
const faceData = await fetch(`/api/face-codes/${characters[0].face_code}/decode`)
    .then(r => r.json());

// 4. Modify morph values in 3D editor...
faceData.components.morph_keys.morph_key_0 = 15;

// 5. Encode back to face code
const newFaceCode = await fetch('/api/face-codes/encode', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({components: faceData.components})
}).then(r => r.json());

// 6. Apply to character
await fetch(`/api/sessions/${session.session_id}/characters/0/face-code`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({face_code: newFaceCode.face_code})
});

// 7. Download modified file
const blob = await fetch(`/api/sessions/${session.session_id}/download`)
    .then(r => r.blob());
```

## **Development Environment Setup**

### **Dependencies**
```bash
pip install fastapi uvicorn python-multipart aiofiles
```

### **Running the API**
```bash
# Development mode with auto-reload
uvicorn appearance.web_api:app --reload --port 8000

# Production mode
uvicorn appearance.web_api:app --host 0.0.0.0 --port 8000
```

### **API Documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

This comprehensive plan provides the foundation for implementing a production-ready FastAPI wrapper that bridges the mb-app functionality with the warband-face-editor web interface.