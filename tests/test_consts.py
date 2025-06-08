from pathlib import Path

import pytest

from appearance.consts import get_profiles_dir_path, get_profiles_file_path


def test_get_profiles_dir_path_windows():
    # Use dependency injection for testing
    test_home = Path("C:/Users/TestUser")
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False, platform="win32", home_path=test_home)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True, platform="win32", home_path=test_home)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_linux():
    # Use dependency injection for testing
    test_home = Path("/home/testuser")
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False, platform="linux", home_path=test_home)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True, platform="linux", home_path=test_home)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_macos():
    # Use dependency injection for testing
    test_home = Path("/Users/testuser")
    
    # Test without WSE2
    result = get_profiles_dir_path(wse2=False, platform="darwin", home_path=test_home)
    expected = Path("/Users/testuser/Library/Application Support/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True, platform="darwin", home_path=test_home)
    expected = Path("/Users/testuser/Library/Application Support/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_dir_path_unknown_platform():
    # Use dependency injection for testing
    test_home = Path("/home/testuser")
    
    # Test fallback for unknown platform
    result = get_profiles_dir_path(wse2=False, platform="unknown_platform", home_path=test_home)
    expected = Path("/home/testuser/Mount&Blade Warband")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_dir_path(wse2=True, platform="unknown_platform", home_path=test_home)
    expected = Path("/home/testuser/Mount&Blade Warband WSE2")
    assert result == expected


def test_get_profiles_file_path_windows():
    # Use dependency injection for testing
    test_home = Path("C:/Users/TestUser")
    
    # Test without WSE2
    result = get_profiles_file_path(wse2=False, platform="win32", home_path=test_home)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband/profiles.dat")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_file_path(wse2=True, platform="win32", home_path=test_home)
    expected = Path("C:/Users/TestUser/AppData/Roaming/Mount&Blade Warband WSE2/profiles.dat")
    assert result == expected


def test_get_profiles_file_path_linux():
    # Use dependency injection for testing
    test_home = Path("/home/testuser")
    
    # Test without WSE2
    result = get_profiles_file_path(wse2=False, platform="linux", home_path=test_home)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband/profiles.dat")
    assert result == expected
    
    # Test with WSE2
    result = get_profiles_file_path(wse2=True, platform="linux", home_path=test_home)
    expected = Path("/home/testuser/.local/share/Mount&Blade Warband WSE2/profiles.dat")
    assert result == expected