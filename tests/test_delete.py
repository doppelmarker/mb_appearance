import pytest
from pathlib import Path
from appearance.service import delete_character
from appearance.helpers import get_header_with_chars_amount


def create_test_profiles_with_characters(tmp_path, num_chars=3):
    """Create a test profiles.dat file with specified number of characters."""
    profiles_path = tmp_path / "profiles.dat"
    
    # Create header with character count
    # Start with a basic 12-byte header
    header = b'\x0a\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00'
    header = get_header_with_chars_amount(header, num_chars)
    
    # Create simple test characters
    characters_data = b""
    for i in range(num_chars):
        name = f"TestChar{i+1}"
        name_bytes = name.encode('utf-8')
        name_length = len(name_bytes)
        
        # Character structure (simplified for testing)
        char_data = bytearray()
        char_data.append(name_length)  # Name length
        char_data.extend(b'\x00' * 3)  # Padding
        char_data.extend(name_bytes)   # Name
        char_data.append(0x00)         # Sex (male)
        char_data.extend(b'\x00' * 4)  # Padding
        char_data.extend(b'\x00' * 4)  # Banner
        char_data.extend(b'\x00')      # Padding
        char_data.extend(b'\x00')      # Skin
        char_data.extend(b'\x00' * 6)  # Padding
        char_data.extend(b'\x00' * 11) # Appearance
        
        # Pad to minimum character size
        while len(char_data) < 89:
            char_data.append(0x00)
        
        characters_data += bytes(char_data)
    
    profiles_path.write_bytes(header + characters_data)
    return profiles_path


def test_delete_character_by_index(tmp_path):
    """Test deleting a character by index."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Delete the middle character (index 1)
    result = delete_character(str(profiles_path), index=1)
    
    assert result is True
    
    # Read the modified file
    data = profiles_path.read_bytes()
    
    # Check header - should now have 2 characters
    assert data[4:8] == b'\x02\x00\x00\x00'  # CHAR_AMOUNT1
    assert data[8:12] == b'\x02\x00\x00\x00'  # CHAR_AMOUNT2
    
    # Check remaining characters
    # First character should still be TestChar1
    assert b'TestChar1' in data
    # Second character should have been deleted
    assert b'TestChar2' not in data
    # Third character should still be there
    assert b'TestChar3' in data


def test_delete_character_by_name(tmp_path):
    """Test deleting a character by name."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Delete character by name
    result = delete_character(str(profiles_path), name="TestChar2")
    
    assert result is True
    
    # Read the modified file
    data = profiles_path.read_bytes()
    
    # Check header - should now have 2 characters
    assert data[4:8] == b'\x02\x00\x00\x00'  # CHAR_AMOUNT1
    assert data[8:12] == b'\x02\x00\x00\x00'  # CHAR_AMOUNT2
    
    # Check remaining characters
    assert b'TestChar1' in data
    assert b'TestChar2' not in data
    assert b'TestChar3' in data


def test_delete_character_invalid_index(tmp_path):
    """Test deleting with invalid index."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Try to delete with out-of-bounds index
    result = delete_character(str(profiles_path), index=5)
    
    assert result is False
    
    # File should be unchanged
    data = profiles_path.read_bytes()
    assert data[4:8] == b'\x03\x00\x00\x00'  # Still 3 characters


def test_delete_character_invalid_name(tmp_path):
    """Test deleting with non-existent name."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Try to delete with non-existent name
    result = delete_character(str(profiles_path), name="NonExistent")
    
    assert result is False
    
    # File should be unchanged
    data = profiles_path.read_bytes()
    assert data[4:8] == b'\x03\x00\x00\x00'  # Still 3 characters


def test_delete_character_no_identifier(tmp_path):
    """Test deleting without specifying index or name."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Try to delete without index or name
    result = delete_character(str(profiles_path))
    
    assert result is False


def test_delete_character_both_identifiers(tmp_path):
    """Test deleting with both index and name (should use index)."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 3)
    
    # Provide both index and name - should use index
    result = delete_character(str(profiles_path), index=0, name="TestChar2")
    
    assert result is True
    
    # Read the modified file
    data = profiles_path.read_bytes()
    
    # TestChar1 (index 0) should be deleted, not TestChar2
    assert b'TestChar1' not in data
    assert b'TestChar2' in data
    assert b'TestChar3' in data


def test_delete_last_character(tmp_path):
    """Test deleting when only one character remains."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 1)
    
    # Try to delete the last character - should fail
    result = delete_character(str(profiles_path), index=0)
    
    assert result is False
    
    # File should be unchanged
    data = profiles_path.read_bytes()
    assert data[4:8] == b'\x01\x00\x00\x00'  # Still 1 character


def test_delete_character_file_not_found():
    """Test deleting from non-existent file."""
    result = delete_character("/non/existent/path/profiles.dat", index=0)
    
    assert result is False


def test_delete_character_preserves_file_structure(tmp_path):
    """Test that deletion preserves the binary structure correctly."""
    profiles_path = create_test_profiles_with_characters(tmp_path, 5)
    
    # Delete a character in the middle
    result = delete_character(str(profiles_path), index=2)
    
    assert result is True
    
    # Read the modified file
    data = profiles_path.read_bytes()
    
    # Check header
    assert data[4:8] == b'\x04\x00\x00\x00'  # Now 4 characters
    assert data[8:12] == b'\x04\x00\x00\x00'
    
    # All other characters should still be present in order
    assert b'TestChar1' in data
    assert b'TestChar2' in data
    assert b'TestChar3' not in data  # This was deleted
    assert b'TestChar4' in data
    assert b'TestChar5' in data