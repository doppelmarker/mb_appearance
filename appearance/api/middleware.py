"""
Custom middleware for the FastAPI web service.

This module provides custom middleware for error handling, logging, and request processing.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from appearance.api.models import ErrorResponse, ValidationErrorResponse, ValidationErrorDetail

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Let FastAPI handle HTTP exceptions normally
            raise
        except ValueError as e:
            logger.error(f"ValueError in {request.url}: {str(e)}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    detail=str(e),
                    error_type="validation_error"
                ).dict()
            )
        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError in {request.url}: {str(e)}")
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    detail="Required file not found",
                    error_type="file_not_found"
                ).dict()
            )
        except PermissionError as e:
            logger.error(f"PermissionError in {request.url}: {str(e)}")
            return JSONResponse(
                status_code=403,
                content=ErrorResponse(
                    detail="Permission denied",
                    error_type="permission_error"
                ).dict()
            )
        except Exception as e:
            logger.error(f"Unexpected error in {request.url}: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    detail="Internal server error",
                    error_type="internal_error"
                ).dict()
            )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url} "
                f"in {process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} for {request.method} {request.url} "
                f"after {process_time:.3f}s"
            )
            raise

class SessionValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for session-based endpoint validation."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is a session-based endpoint
        if "/api/sessions/" in str(request.url.path) and request.url.path != "/api/sessions":
            # Extract session_id from path
            path_parts = request.url.path.split('/')
            try:
                sessions_index = path_parts.index('sessions')
                if len(path_parts) > sessions_index + 1:
                    session_id = path_parts[sessions_index + 1]
                    
                    # Validate session ID format (UUID)
                    import uuid
                    try:
                        uuid.UUID(session_id)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content=ErrorResponse(
                                detail="Invalid session ID format",
                                error_type="validation_error"
                            ).dict()
                        )
            except (ValueError, IndexError):
                pass
        
        return await call_next(request)

# Utility functions for error handling
def create_validation_error_response(errors: list) -> JSONResponse:
    """Create a standardized validation error response."""
    error_details = []
    for error in errors:
        error_details.append(ValidationErrorDetail(
            field=error.get('field', 'unknown'),
            message=error.get('message', 'Validation failed'),
            invalid_value=str(error.get('value', ''))
        ))
    
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            errors=error_details
        ).dict()
    )

def handle_face_code_error(face_code: str, error_msg: str) -> JSONResponse:
    """Handle face code specific errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            detail=f"Face code error: {error_msg}",
            error_type="face_code_error",
            field="face_code"
        ).dict()
    )

def handle_character_not_found_error(character_index: int) -> JSONResponse:
    """Handle character not found errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail=f"Character at index {character_index} not found",
            error_type="character_not_found",
            field="character_index"
        ).dict()
    )

def handle_session_not_found_error(session_id: str) -> JSONResponse:
    """Handle session not found errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail=f"Session {session_id} not found",
            error_type="session_not_found",
            field="session_id"
        ).dict()
    )