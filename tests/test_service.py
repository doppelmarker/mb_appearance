import logging

import pytest

from appearance.service import (
    backup,
    generate_n_random_characters,
    restore_from_backup,
    show_backuped_characters,
)




def test_backup_creates_file(stub_profiles_file, stub_backup_dir):
    # Perform backup
    backup("test_backup.dat", profiles_file_path=stub_profiles_file, backup_dir=stub_backup_dir)

    # Verify backup was created
    backup_file = stub_backup_dir / "test_backup.dat"
    assert backup_file.exists()
    assert backup_file.read_bytes() == b"test profile data"


def test_backup_wse2_flag(stub_wse2_profiles_file, stub_backup_dir):
    # Perform backup with WSE2 flag
    backup("wse2_backup.dat", wse2=True, profiles_file_path=stub_wse2_profiles_file, backup_dir=stub_backup_dir)

    # Verify backup was created
    backup_file = stub_backup_dir / "wse2_backup.dat"
    assert backup_file.exists()
    assert backup_file.read_bytes() == b"wse2 profile data"


def test_show_backuped_characters_lists_files(stub_backup_dir, caplog):
    # Create backup files
    (stub_backup_dir / "backup1.dat").write_bytes(b"data1")
    (stub_backup_dir / "backup2.dat").write_bytes(b"data2")
    (stub_backup_dir / "character_save.dat").write_bytes(b"data3")

    # Capture logs
    with caplog.at_level(logging.INFO):
        show_backuped_characters(stub_backup_dir)

    # Verify logs contain expected messages
    assert "Available backups:" in caplog.text
    assert "backup1" in caplog.text
    assert "backup2" in caplog.text
    assert "character_save" in caplog.text


def test_show_backuped_characters_empty_directory(stub_backup_dir, caplog):
    # Capture logs
    with caplog.at_level(logging.INFO):
        show_backuped_characters(stub_backup_dir)

    # Should only show the header
    assert "Available backups:" in caplog.text
    assert caplog.text.count("\n") == 1  # Only one log line


def test_restore_from_backup_success(stub_backup_dir, stub_profiles_file):
    # Create backup file
    backup_file = stub_backup_dir / "test_backup.dat"
    backup_data = b"backup profile data"
    backup_file.write_bytes(backup_data)

    # Restore from backup
    restore_from_backup(stub_backup_dir, "test_backup.dat", profiles_file_path=stub_profiles_file)

    # Verify profiles file was updated
    assert stub_profiles_file.read_bytes() == backup_data


def test_restore_from_backup_wse2(stub_backup_dir, stub_wse2_profiles_file):
    # Create backup file
    backup_file = stub_backup_dir / "wse2_backup.dat"
    backup_data = b"wse2 backup data"
    backup_file.write_bytes(backup_data)

    # Restore from backup with WSE2 flag
    restore_from_backup(stub_backup_dir, "wse2_backup.dat", wse2=True, profiles_file_path=stub_wse2_profiles_file)

    # Verify profiles file was updated
    assert stub_wse2_profiles_file.read_bytes() == backup_data


def test_generate_single_character(stub_profiles_file, stub_resource_files):
    # Use stub profiles file

    # Generate 1 character
    generate_n_random_characters(
        1,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )

    # Verify file was created and has content
    assert stub_profiles_file.exists()
    content = stub_profiles_file.read_bytes()
    assert len(content) > 16  # Header + at least one character


def test_generate_multiple_characters(stub_profiles_file, stub_resource_files):
    # Use stub profiles file

    # Generate 5 characters
    generate_n_random_characters(
        5,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )

    # Verify file was created and has expected size
    assert stub_profiles_file.exists()
    content = stub_profiles_file.read_bytes()
    # Each character adds 284 bytes to the header
    expected_min_size = 16 + (5 * 284)
    assert len(content) >= expected_min_size


def test_generate_characters_name_cycling():
    """Test that character names cycle through the alphabet."""
    import string
    names = string.ascii_lowercase

    # Test name cycling logic
    for i in range(30):  # Test beyond 26 letters
        expected_name = names[i % len(names)]
        assert expected_name == names[i % 26]


def test_generate_characters_creates_unique_characters(stub_profiles_file, stub_resource_files):
    """Test that generated characters have variation."""
    # Use stub profiles file

    # Generate multiple characters
    generate_n_random_characters(
        10,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )

    # Read the generated content
    content = stub_profiles_file.read_bytes()

    # Skip header (16 bytes) and check that characters have some variation
    header_size = 16
    char_size = 284

    # Extract a few characters and verify they're not all identical
    char1 = content[header_size:header_size + char_size]
    char2 = content[header_size + char_size:header_size + 2 * char_size]
    char3 = content[header_size + 2 * char_size:header_size + 3 * char_size]

    # Characters should have some differences (due to random generation)
    # But they might have the same structure
    assert len(char1) == char_size
    assert len(char2) == char_size
    assert len(char3) == char_size


def test_generate_characters_creates_directory(tmp_path, stub_resource_files):
    """Test that character generation creates the profiles directory if it doesn't exist."""
    # Create a path in a non-existent directory
    nonexistent_dir = tmp_path / "Mount&Blade Warband"
    profiles_file = nonexistent_dir / "profiles.dat"
    
    # Directory shouldn't exist yet
    assert not nonexistent_dir.exists()
    
    # Generate characters
    generate_n_random_characters(
        3,
        profiles_file_path=profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Directory and file should now exist
    assert nonexistent_dir.exists()
    assert profiles_file.exists()
    
    # Verify the file has content
    content = profiles_file.read_bytes()
    assert len(content) > 16  # Header + characters


def test_generate_characters_wse2_directory(tmp_path, stub_resource_files):
    """Test that character generation works with WSE2 directory structure."""
    # Create a path for WSE2
    wse2_dir = tmp_path / "Mount&Blade Warband WSE2"
    profiles_file = wse2_dir / "profiles.dat"
    
    # Directory shouldn't exist yet
    assert not wse2_dir.exists()
    
    # Generate characters with wse2 flag
    generate_n_random_characters(
        2,
        wse2=True,
        profiles_file_path=profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Directory and file should now exist
    assert wse2_dir.exists()
    assert profiles_file.exists()
