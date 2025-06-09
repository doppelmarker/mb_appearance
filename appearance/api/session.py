"""
Session management for the FastAPI web service.

This module handles temporary file storage, session lifecycle, and cleanup.
"""

import asyncio
import uuid
import tempfile
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from appearance.helpers import read_profiles, write_profiles

# Configuration
SESSION_TIMEOUT = timedelta(hours=2)

class SessionData:
    """Data stored for each session."""
    
    def __init__(self, profiles_data: bytes):
        self.profiles_data = profiles_data
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.backups: List[bytes] = []
        self.temp_dir = tempfile.mkdtemp(prefix="mb_session_")

    def update_access_time(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.utcnow()

    def get_profiles_path(self) -> str:
        """Get path to temporary profiles.dat file."""
        return os.path.join(self.temp_dir, "profiles.dat")

    def save_profiles_to_temp(self) -> str:
        """Save current profiles data to temporary file and return path."""
        temp_path = self.get_profiles_path()
        write_profiles(temp_path, self.profiles_data)
        return temp_path

    def load_profiles_from_temp(self):
        """Load profiles data from temporary file."""
        temp_path = self.get_profiles_path()
        if os.path.exists(temp_path):
            self.profiles_data = read_profiles(temp_path)
            self.update_access_time()

    def add_backup(self, backup_data: Optional[bytes] = None):
        """Add backup of current or specified data."""
        data_to_backup = backup_data if backup_data is not None else self.profiles_data
        self.backups.append(data_to_backup)
        self.update_access_time()

    def get_latest_backup(self) -> Optional[bytes]:
        """Get the most recent backup."""
        return self.backups[-1] if self.backups else None

    def restore_from_backup(self, backup_index: int = -1) -> bool:
        """Restore from backup by index (default: latest)."""
        if not self.backups:
            return False
        
        try:
            backup_data = self.backups[backup_index]
            self.profiles_data = backup_data
            self.update_access_time()
            return True
        except IndexError:
            return False

    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

class SessionStorage:
    """Thread-safe session storage manager."""
    
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, profiles_data: Optional[bytes] = None) -> str:
        """Create a new session with optional initial data."""
        session_id = str(uuid.uuid4())
        
        if profiles_data is None:
            # Create empty session with minimal profiles data (header only)
            from appearance.consts import HEADER_FILE_PATH
            profiles_data = read_profiles(HEADER_FILE_PATH)
        
        async with self._lock:
            self._sessions[session_id] = SessionData(profiles_data)
        
        return session_id

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data and update access time."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.update_access_time()
            return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete session and clean up resources."""
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                session.cleanup()
                return True
            return False

    async def update_session_data(self, session_id: str, profiles_data: bytes) -> bool:
        """Update session profiles data."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.profiles_data = profiles_data
                session.update_access_time()
                return True
            return False

    async def add_backup(self, session_id: str, backup_data: Optional[bytes] = None) -> bool:
        """Add backup to session."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.add_backup(backup_data)
                return True
            return False

    async def restore_from_backup(self, session_id: str, backup_index: int = -1) -> bool:
        """Restore session from backup."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.restore_from_backup(backup_index)
            return False

    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return {
                    'session_id': session_id,
                    'created_at': session.created_at,
                    'last_accessed': session.last_accessed,
                    'backup_count': len(session.backups),
                    'has_backups': len(session.backups) > 0
                }
            return None

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of cleaned sessions."""
        cutoff = datetime.utcnow() - SESSION_TIMEOUT
        expired_sessions = []
        
        async with self._lock:
            for session_id, session in list(self._sessions.items()):
                if session.last_accessed < cutoff:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                session = self._sessions.pop(session_id, None)
                if session:
                    session.cleanup()
        
        return len(expired_sessions)

    async def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        async with self._lock:
            return len(self._sessions)

    async def get_session_ids(self) -> List[str]:
        """Get list of active session IDs."""
        async with self._lock:
            return list(self._sessions.keys())

# Global session storage instance
_session_storage: Optional[SessionStorage] = None

def get_session_storage() -> SessionStorage:
    """Get the global session storage instance."""
    global _session_storage
    if _session_storage is None:
        _session_storage = SessionStorage()
    return _session_storage

# Utility functions for session validation
def validate_profiles_format(data: bytes) -> bool:
    """Validate that uploaded data is a valid profiles.dat format."""
    if len(data) < 12:  # Minimum header size
        return False
    
    # Check if we can read character count from header
    try:
        char_count = int.from_bytes(data[4:8], byteorder='little')
        # Reasonable limits check
        if char_count < 0 or char_count > 1000:
            return False
        return True
    except Exception:
        return False

# Background task for session cleanup
async def session_cleanup_task(storage: SessionStorage):
    """Background task to clean up expired sessions."""
    while True:
        try:
            cleaned_count = await storage.cleanup_expired_sessions()
            if cleaned_count > 0:
                print(f"Cleaned up {cleaned_count} expired sessions")
        except Exception as e:
            print(f"Error during session cleanup: {e}")
        
        # Sleep for 1 hour between cleanup runs
        await asyncio.sleep(3600)