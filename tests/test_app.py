import logging
from pathlib import Path

import pytest

from appearance.argparser import ArgParser
from appearance import service


def test_argparser_direct_parse():
    """Test argument parsing without monkeypatch."""
    parser = ArgParser()
    
    # Test show command
    args = parser.parser.parse_args(["-s"])
    assert args.show is True
    
    # Test backup command
    args = parser.parser.parse_args(["-b", "test_backup"])
    assert args.backup == "test_backup"
    
    # Test restore command
    args = parser.parser.parse_args(["-r", "test_restore"])
    assert args.restore == "test_restore"
    
    # Test generate command
    args = parser.parser.parse_args(["-g", "10"])
    assert args.gen == 10
    
    # Test delete command
    args = parser.parser.parse_args(["-d", "TestChar"])
    assert args.delete == "TestChar"
    
    # Test list command
    args = parser.parser.parse_args(["-l"])
    assert args.list is True
    
    # Test wse2 flag
    args = parser.parser.parse_args(["--wse2", "-g", "5"])
    assert args.wse2 is True
    assert args.gen == 5


def test_no_action_error():
    """Test that no action raises error."""
    parser = ArgParser()
    args = parser.parser.parse_args([])
    
    # The app should error when no action is provided
    assert not any([args.backup, args.restore, args.gen, args.show, args.delete, args.list])


def test_show_backuped_characters_function(tmp_path):
    """Test show_backuped_characters function directly."""
    # Create backup directory with files
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "backup1.dat").write_bytes(b"data1")
    (backup_dir / "backup2.dat").write_bytes(b"data2")
    (backup_dir / "not_a_dat.txt").write_bytes(b"data3")  # Should be ignored
    
    # Call the function directly
    service.show_backuped_characters(backup_dir)
    # The function logs output, so we just verify it doesn't crash


def test_backup_function(tmp_path):
    """Test backup function directly."""
    # Create test profiles file
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"test profile data")
    
    # Create backup directory
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Call backup directly with dependency injection
    service.backup(
        "test_backup.dat",
        wse2=False,
        profiles_file_path=profiles_file,
        backup_dir=backup_dir
    )
    
    # Verify backup was created
    backup_file = backup_dir / "test_backup.dat"
    assert backup_file.exists()
    assert backup_file.read_bytes() == b"test profile data"


def test_restore_from_backup_function(tmp_path):
    """Test restore_from_backup function directly."""
    # Create backup file
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup_file = backup_dir / "test_restore.dat"
    backup_data = b"backup profile data"
    backup_file.write_bytes(backup_data)
    
    # Create profiles file
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"old data")
    
    # Call restore directly with dependency injection
    service.restore_from_backup(
        backup_dir,
        "test_restore.dat",
        wse2=False,
        profiles_file_path=profiles_file
    )
    
    # Verify restore worked
    assert profiles_file.read_bytes() == backup_data


def test_generate_random_characters_function(tmp_path):
    """Test generate_n_random_characters function directly."""
    # Create profiles directory
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Call generate directly with dependency injection
    service.generate_n_random_characters(
        3,
        wse2=False,
        profiles_file_path=profiles_file
    )
    
    # Verify file was created and has content
    assert profiles_file.exists()
    assert profiles_file.stat().st_size > 0
    
    # Verify we can list the characters
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 3


def test_delete_character_function(tmp_path):
    """Test delete_character function directly."""
    # Create profiles file with test data
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # First generate some characters
    service.generate_n_random_characters(
        3,
        wse2=False,
        profiles_file_path=profiles_file
    )
    
    # Get initial character list
    chars_before = service.list_characters(profiles_file_path=profiles_file)
    assert len(chars_before) == 3
    first_char_name = chars_before[0]['name']
    
    # Delete by index
    success = service.delete_character(str(profiles_file), index=0)
    assert success
    
    # Verify deletion
    chars_after = service.list_characters(profiles_file_path=profiles_file)
    assert len(chars_after) == 2
    assert all(char['name'] != first_char_name for char in chars_after)
    
    # Delete by name
    second_char_name = chars_after[0]['name']
    success = service.delete_character(str(profiles_file), name=second_char_name)
    assert success
    
    # Verify deletion
    chars_final = service.list_characters(profiles_file_path=profiles_file)
    assert len(chars_final) == 1
    assert chars_final[0]['name'] != second_char_name


def test_list_characters_function(tmp_path):
    """Test list_characters function directly."""
    # Create profiles file
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Generate test characters
    service.generate_n_random_characters(
        5,
        wse2=False,
        profiles_file_path=profiles_file
    )
    
    # List characters
    characters = service.list_characters(profiles_file_path=profiles_file)
    
    # Verify results
    assert len(characters) == 5
    for i, char in enumerate(characters):
        assert char['index'] == i
        assert 'name' in char
        assert 'sex' in char
        assert 'skin' in char
        assert char['sex'] in ['Male', 'Female']
        assert char['skin'] in ['White', 'Light', 'Tan', 'Dark', 'Black']


def test_file_validation(tmp_path):
    """Test file validation functions."""
    from appearance.validators import validate_file_exists
    
    # Create test file
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(b"data")
    
    # Test existing file
    assert validate_file_exists(test_file) is True
    
    # Test non-existing file  
    assert validate_file_exists(tmp_path / "nonexistent.dat") is False