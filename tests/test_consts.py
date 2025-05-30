import sys
from pathlib import Path

import pytest

from appearance.consts import get_profiles_dir_path, get_profiles_file_path


def test_get_profiles_dir_path_windows(monkeypatch):
    # Mock Windows platform
    monkeypatch.setattr(sys, "platform", "win32")
    
    # Mock home directory
    def mock_home():
        return Path("C:/Users/TestUser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_linux(monkeypatch):
    # Mock Linux platform
    monkeypatch.setattr(sys, "platform", "linux")
    
    # Mock home directory
    def mock_home():
        return Path("/home/testuser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_macos(monkeypatch):
    # Mock macOS platform
    monkeypatch.setattr(sys, "platform", "darwin")
    
    # Mock home directory
    def mock_home():
        return Path("/Users/testuser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False)
    expected = Path("/Users/testuser/Library/Application Support/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True)
    expected = Path("/Users/testuser/Library/Application Support/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_unknown_platform(monkeypatch):
    # Mock unknown platform
    monkeypatch.setattr(sys, "platform", "unknown_platform")
    
    # Mock home directory
    def mock_home():
        return Path("/home/testuser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test fallback for unknown platform
    result = get_profiles_dir_path(wse2=False)
    expected = Path("/home/testuser/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True)
    expected = Path("/home/testuser/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_file_path_windows(monkeypatch):
    # Mock Windows platform
    monkeypatch.setattr(sys, "platform", "win32")
    
    # Mock home directory
    def mock_home():
        return Path("C:/Users/TestUser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test without WSE2
    result = get_profiles_file_path(wse2=False)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband/profiles.dat")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_file_path(wse2=True)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband WSE2/profiles.dat")
    assert result == expected


def test_get_profiles_file_path_linux(monkeypatch):
    # Mock Linux platform
    monkeypatch.setattr(sys, "platform", "linux")
    
    # Mock home directory
    def mock_home():
        return Path("/home/testuser")
    monkeypatch.setattr(Path, "home", mock_home)
    
    # Test without WSE2
    result = get_profiles_file_path(wse2=False)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband/profiles.dat")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_file_path(wse2=True)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband WSE2/profiles.dat")
    assert result == expected