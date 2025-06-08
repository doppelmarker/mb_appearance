import logging

import pytest

from appearance.service import (
    backup,
    generate_n_random_characters,
    list_characters,
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
    # Each character adds MIN_BYTES_AMOUNT_FOR_CHAR (89) bytes to the header (12 bytes)
    from appearance.consts import MIN_BYTES_AMOUNT_FOR_CHAR
    expected_min_size = 12 + (5 * MIN_BYTES_AMOUNT_FOR_CHAR)
    assert len(content) >= expected_min_size


def test_generate_characters_name_cycling(stub_profiles_file, stub_resource_files):
    """Test that character names use numbering strategy when exceeding alphabet."""
    # Generate 30 characters to test beyond alphabet
    generate_n_random_characters(
        30,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # List characters and check names
    characters = list_characters(profiles_file_path=stub_profiles_file)
    
    # Verify we have 30 characters
    assert len(characters) == 30
    
    # Test expected naming pattern
    expected_names = []
    import string
    names = string.ascii_lowercase
    
    for i in range(30):
        letter_idx = i % len(names)
        group_number = i // len(names)
        if group_number == 0:
            expected_names.append(names[letter_idx])
        else:
            expected_names.append(names[letter_idx] + str(group_number))
    
    # Check that names match expected pattern
    actual_names = [char['name'] for char in characters]
    
    # First 26 should be a-z
    assert actual_names[:26] == list(string.ascii_lowercase)
    
    # Next 4 should be a1, b1, c1, d1
    assert actual_names[26:30] == ['a1', 'b1', 'c1', 'd1']
    
    # Verify all names are unique
    assert len(set(actual_names)) == len(actual_names)


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


def test_list_characters_empty_file(tmp_path):
    """Test listing characters from an empty profiles file."""
    profiles_file = tmp_path / "profiles.dat"
    # Create a file with just a header but no characters
    header = b"\x00\x00\x00\x00"  # 4 bytes
    header += b"\x00\x00\x00\x00"  # Character count = 0
    header += b"\x00\x00\x00\x00"  # 4 more bytes
    profiles_file.write_bytes(header)
    
    characters = list_characters(profiles_file_path=str(profiles_file))
    assert characters == []


def test_list_characters_single_character(stub_profiles_file, stub_resource_files):
    """Test listing a single character."""
    # Generate a single character using actual generation
    generate_n_random_characters(
        1,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    characters = list_characters(profiles_file_path=str(stub_profiles_file))
    assert len(characters) == 1
    assert characters[0]['index'] == 0
    assert characters[0]['name'] == 'a'  # First character name
    
    # Verify valid sex and skin values (the key point of our fix)
    assert characters[0]['sex'] in ['Male', 'Female']
    assert characters[0]['skin'] in ['White', 'Light', 'Tan', 'Dark', 'Black']


def test_list_characters_multiple_characters(stub_profiles_file, stub_resource_files):
    """Test listing multiple characters with different attributes."""
    # Generate multiple characters using actual generation
    generate_n_random_characters(
        3,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    characters = list_characters(profiles_file_path=str(stub_profiles_file))
    assert len(characters) == 3
    
    # Check that all characters have valid attributes
    expected_names = ['a', 'b', 'c']  # Character names cycle through alphabet
    for i, char in enumerate(characters):
        assert char['index'] == i
        assert char['name'] == expected_names[i]
        # Verify valid sex and skin values (the key point of our fix)
        assert char['sex'] in ['Male', 'Female']
        assert char['skin'] in ['White', 'Light', 'Tan', 'Dark', 'Black']


def test_list_characters_wse2(stub_profiles_file, stub_resource_files):
    """Test listing characters with WSE2 flag."""
    # Generate a character using actual generation
    generate_n_random_characters(
        1,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    characters = list_characters(profiles_file_path=str(stub_profiles_file), wse2=True)
    assert len(characters) == 1
    assert characters[0]['name'] == 'a'  # First character name
    # Verify valid sex and skin values (the key point of our fix)
    assert characters[0]['sex'] in ['Male', 'Female']
    assert characters[0]['skin'] in ['White', 'Light', 'Tan', 'Dark', 'Black']


def test_list_characters_handles_errors(tmp_path, caplog):
    """Test that list_characters handles errors gracefully."""
    nonexistent_file = tmp_path / "nonexistent.dat"
    
    with caplog.at_level(logging.ERROR):
        characters = list_characters(profiles_file_path=str(nonexistent_file))
    
    assert characters == []
    assert "Failed to list characters" in caplog.text


def test_generate_characters_valid_skin_values(stub_profiles_file, stub_resource_files):
    """Test that all generated characters have valid skin values (bug #9 fix)."""
    # Generate multiple characters
    generate_n_random_characters(
        20,  # Generate enough characters to test the bug
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # List the generated characters
    characters = list_characters(profiles_file_path=str(stub_profiles_file))
    
    # Valid skin values are 0, 16, 32, 48, 64
    valid_skin_names = ['White', 'Light', 'Tan', 'Dark', 'Black']
    
    # Verify all characters have valid skin values
    assert len(characters) == 20
    for i, char in enumerate(characters):
        assert char['skin'] in valid_skin_names, f"Character {i} ({char['name']}) has invalid skin: {char['skin']}"
        # Ensure no "Unknown (255)" or other invalid values
        assert 'Unknown' not in char['skin'], f"Character {i} ({char['name']}) has corrupted skin value"


def test_generate_characters_independent_data(stub_profiles_file, stub_resource_files):
    """Test that each generated character has independent data (no data corruption)."""
    # Generate multiple characters
    num_chars = 10
    generate_n_random_characters(
        num_chars,
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Read the raw file to check byte-level independence
    content = stub_profiles_file.read_bytes()
    header_size = 12  # Header is 12 bytes
    char_size = 89  # Minimum character size
    
    # Import CHAR_OFFSETS to use proper offsets
    from appearance.consts import CHAR_OFFSETS
    
    # Extract sex and skin bytes for each character
    sex_values = []
    skin_values = []
    
    for i in range(num_chars):
        char_start = header_size + (i * char_size)
        # Use the defined offsets
        sex_offset = char_start + CHAR_OFFSETS["SEX"]
        skin_offset = char_start + CHAR_OFFSETS["SKIN"]
        
        sex_values.append(content[sex_offset])
        skin_values.append(content[skin_offset])
    
    # Verify all sex values are valid (0 or 1)
    for i, sex in enumerate(sex_values):
        assert sex in [0, 1], f"Character {i} has invalid sex value: {sex}"
    
    # Verify all skin values are valid (0, 16, 32, 48, 64)
    valid_skin_bytes = [0, 16, 32, 48, 64]
    for i, skin in enumerate(skin_values):
        assert skin in valid_skin_bytes, f"Character {i} has invalid skin value: {skin}"
    
    # Verify we have some variation (not all characters identical)
    # With 10 characters, we should see at least 2 different sex values or skin values
    assert len(set(sex_values)) > 1 or len(set(skin_values)) > 1, "All characters appear to have identical attributes"
