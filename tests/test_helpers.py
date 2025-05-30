from pathlib import Path

import pytest

from appearance.helpers import (
    get_header_with_chars_amount,
    get_name_length,
    get_random_byte_between,
    get_random_byte_for_idx,
    get_random_sex,
    get_random_skin,
    int_to_hex_bytes,
    read_profiles,
    write_profiles,
)


def test_int_to_hex_bytes_single_byte():
    assert int_to_hex_bytes(0) == b"\x00"
    assert int_to_hex_bytes(255) == b"\xff"
    assert int_to_hex_bytes(127) == b"\x7f"


def test_int_to_hex_bytes_two_bytes():
    assert int_to_hex_bytes(256) == b"\x00\x01"
    assert int_to_hex_bytes(65535) == b"\xff\xff"


def test_int_to_hex_bytes_three_bytes():
    assert int_to_hex_bytes(65536) == b"\x00\x00\x01"
    assert int_to_hex_bytes(16777215) == b"\xff\xff\xff"


def test_int_to_hex_bytes_four_bytes():
    assert int_to_hex_bytes(16777216) == b"\x00\x00\x00\x01"
    assert int_to_hex_bytes(4294967295) == b"\xff\xff\xff\xff"


def test_int_to_hex_bytes_invalid_values():
    with pytest.raises(ValueError):
        int_to_hex_bytes(-1)
    with pytest.raises(ValueError):
        int_to_hex_bytes(4294967296)


def test_read_profiles(tmp_path):
    # Create a test file with known content
    test_file = tmp_path / "test_profiles.dat"
    test_data = b"test profile data"
    test_file.write_bytes(test_data)

    # Read and verify
    data = read_profiles(test_file)
    assert data == test_data


def test_write_profiles(tmp_path):
    test_data = b"test profile data"
    test_file = tmp_path / "test_profiles.dat"

    write_profiles(test_file, test_data)

    assert test_file.exists()
    assert test_file.read_bytes() == test_data


def test_write_profiles_creates_directory(tmp_path):
    # Test that write_profiles creates parent directories
    test_data = b"test profile data"
    test_file = tmp_path / "nonexistent" / "directory" / "test_profiles.dat"
    
    # Directory shouldn't exist yet
    assert not test_file.parent.exists()
    
    write_profiles(test_file, test_data)
    
    # Directory should be created and file written
    assert test_file.parent.exists()
    assert test_file.exists()
    assert test_file.read_bytes() == test_data


def test_write_profiles_handles_existing_directory(tmp_path):
    # Test that write_profiles works when directory already exists
    test_data = b"test profile data"
    nested_dir = tmp_path / "existing" / "directory"
    nested_dir.mkdir(parents=True)
    test_file = nested_dir / "test_profiles.dat"
    
    write_profiles(test_file, test_data)
    
    assert test_file.exists()
    assert test_file.read_bytes() == test_data


def test_read_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        read_profiles(Path("/nonexistent/file.dat"))


def test_get_name_length_with_null_terminator(tmp_path):
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(b"header" + b"PlayerName\x00" + b"remaining")

    length = get_name_length(test_file, 6)  # Start of 'PlayerName'
    assert length == 10


def test_get_name_length_with_one_terminator(tmp_path):
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(b"header" + b"Name\x01" + b"remaining")

    length = get_name_length(test_file, 6)  # Start of 'Name'
    assert length == 4


def test_get_name_length_empty_name(tmp_path):
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(b"header" + b"\x00" + b"remaining")

    length = get_name_length(test_file, 6)
    assert length == 0


def test_get_name_length_at_eof(tmp_path):
    test_file = tmp_path / "test.dat"
    test_file.write_bytes(b"short")

    # When seeking beyond file, read returns empty bytes
    length = get_name_length(test_file, 5)  # Exactly at EOF
    assert length == 0


def test_get_header_with_chars_amount():
    # Create a header with placeholder values at known offsets
    # Based on HEADER_OFFSETS from consts.py
    header = b"\x00" * 16  # 16 byte header

    # Update with 5 characters
    result = get_header_with_chars_amount(header, 5)

    # Should have updated the header with the character count
    assert len(result) == 16
    # Check that the header was modified (not all zeros)
    assert result != header


def test_get_header_with_chars_amount_zero_chars():
    header = b"\xff" * 16
    result = get_header_with_chars_amount(header, 0)
    assert len(result) == 16


def test_get_header_with_chars_amount_large_number():
    header = b"\x00" * 16
    result = get_header_with_chars_amount(header, 1000)
    assert len(result) == 16


def test_get_random_byte_for_idx_single_byte_indices():
    # Test indices 0-6, 8-9 (random single byte)
    for idx in [0, 1, 2, 3, 4, 5, 6, 8, 9]:
        result = get_random_byte_for_idx(idx)
        assert isinstance(result, bytes)
        assert len(result) == 1


def test_get_random_byte_for_idx_limited_range():
    # Test index 7 (0-127 range)
    for _ in range(10):
        result = get_random_byte_for_idx(7)
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert 0 <= ord(result) <= 127


def test_get_random_byte_for_idx_small_range():
    # Test other indices (28-31 range)
    for idx in [10, 11, 15, 20]:
        result = get_random_byte_for_idx(idx)
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert 28 <= ord(result) <= 31


def test_get_random_byte_between():
    # Test various ranges
    for _ in range(10):
        result = get_random_byte_between(0, 127)
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert 0 <= ord(result) <= 127

    # Test specific range
    for _ in range(10):
        result = get_random_byte_between(28, 31)
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert 28 <= ord(result) <= 31


def test_get_random_sex():
    # Should only return male or female bytes
    results = set()
    for _ in range(20):
        result = get_random_sex()
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert result in (b"\x00", b"\x01")
        results.add(result)

    # Should eventually return both values
    assert len(results) == 2


def test_get_random_skin():
    # Should only return valid skin color bytes
    valid_skins = (b"\x00", b"\x10", b"\x20", b"\x30", b"\x40")
    results = set()

    for _ in range(50):
        result = get_random_skin()
        assert isinstance(result, bytes)
        assert len(result) == 1
        assert result in valid_skins
        results.add(result)

    # Should eventually return all skin types
    assert len(results) == 5
