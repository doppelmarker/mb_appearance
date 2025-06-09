"""
FastAPI Web Service Entry Point for Mount & Blade Warband Face Editor

This module provides the main entry point for the web API server.
"""

import uvicorn
from appearance.api.app import app

# Export the app for use with uvicorn
__all__ = ['app']

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "appearance.web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )