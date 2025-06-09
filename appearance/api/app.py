"""
Main FastAPI application for Mount & Blade Warband Face Editor.

This module creates the FastAPI app and includes all route modules.
"""

import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from appearance.api.models import HealthResponse, ErrorResponse
from appearance.api.session import get_session_storage, session_cleanup_task
from appearance.api import characters, face_codes, files
from appearance.api.middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    SessionValidationMiddleware
)

# Create FastAPI app
app = FastAPI(
    title="Mount & Blade Warband Face Editor API",
    description="REST API for manipulating Mount & Blade character appearance data and face codes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add custom middleware (order matters - first added is outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SessionValidationMiddleware)

# CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(characters.router)
app.include_router(face_codes.router)
app.include_router(files.router)

# Session management endpoints
@app.post("/api/sessions")
async def create_session():
    """Create a new session."""
    storage = get_session_storage()
    session_id = await storage.create_session()
    
    session_info = await storage.get_session_info(session_id)
    
    return {
        "session_id": session_id,
        "character_count": 0,
        "created_at": session_info['created_at'],
        "last_accessed": session_info['last_accessed'],
        "has_backups": False
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    storage = get_session_storage()
    session_info = await storage.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get character count
    session = await storage.get_session(session_id)
    if session:
        try:
            from appearance.service import list_characters
            temp_path = session.save_profiles_to_temp()
            characters = list_characters(profiles_file_path=temp_path)
            char_count = len(characters)
        except Exception:
            char_count = 0
    else:
        char_count = 0
    
    return {
        "session_id": session_id,
        "character_count": char_count,
        "created_at": session_info['created_at'],
        "last_accessed": session_info['last_accessed'],
        "has_backups": session_info['has_backups']
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    storage = get_session_storage()
    success = await storage.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

# Health and status endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.get("/api/status")
async def api_status():
    """Get API status and statistics."""
    storage = get_session_storage()
    active_sessions = await storage.get_active_session_count()
    
    return {
        "status": "running",
        "version": "1.0.0",
        "active_sessions": active_sessions,
        "timestamp": datetime.utcnow()
    }

# Custom exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            detail=str(exc),
            error_type="value_error"
        ).dict()
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    """Handle FileNotFoundError exceptions."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail="File not found",
            error_type="file_not_found"
        ).dict()
    )

# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    print("Starting Mount & Blade Warband Face Editor API...")
    
    # Start background session cleanup task
    storage = get_session_storage()
    asyncio.create_task(session_cleanup_task(storage))
    
    print("API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    print("Shutting down Mount & Blade Warband Face Editor API...")
    
    # Clean up all active sessions
    storage = get_session_storage()
    session_ids = await storage.get_session_ids()
    
    for session_id in session_ids:
        await storage.delete_session(session_id)
    
    print("API shutdown complete!")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Mount & Blade Warband Face Editor API",
        "version": "1.0.0",
        "description": "REST API for manipulating Mount & Blade character appearance data",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health"
    }