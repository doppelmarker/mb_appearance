
import pytest


@pytest.fixture
def stub_profiles_file(tmp_path):
    """Create a stub profiles.dat file for testing."""
    profiles_file = tmp_path / "profiles.dat"
    profiles_file.write_bytes(b"test profile data")
    return profiles_file


@pytest.fixture
def stub_wse2_profiles_file(tmp_path):
    """Create a stub profiles_wse2.dat file for testing."""
    profiles_file = tmp_path / "profiles_wse2.dat"
    profiles_file.write_bytes(b"wse2 profile data")
    return profiles_file


@pytest.fixture
def stub_backup_dir(tmp_path):
    """Create a stub backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir


@pytest.fixture
def stub_resources_dir(tmp_path):
    """Create a stub resources directory."""
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    return resources_dir


@pytest.fixture
def stub_resource_files(tmp_path):
    """Create stub resource files for testing."""
    # Create a stub header file
    header_file = tmp_path / "header.dat"
    # Header: 4 bytes + char_count(4) + char_count(4) = 12 bytes total
    header_data = b"\x00\x00\x00\x00"  # 4 bytes
    header_data += b"\x00\x00\x00\x00"  # Character count = 0
    header_data += b"\x00\x00\x00\x00"  # Character count = 0 (duplicate)
    header_file.write_bytes(header_data)

    # Create a stub common_char file with a realistic character template
    common_char_file = tmp_path / "common_char.dat"
    # 12 bytes offset (header-like data)
    char_data = b"\x00" * 12
    
    # Character template (starts at offset 12):
    # name_length (1 byte) + padding (3 bytes) + name + rest of data
    template = b"\x01"  # name length = 1
    template += b"\x00\x00\x00"  # padding
    template += b"a"  # name
    template += b"\x00"  # sex (offset 5 from char start) = male
    template += b"\x00\x00\x00"  # 3 bytes padding
    template += b"\x00\x00\x00\x00"  # banner (offset 9) - 4 bytes
    template += b"\x00"  # skin (offset 14 from char start) = white
    template += b"\x00" * 6  # padding before appearance
    template += b"\x00" * 11  # appearance bytes (offset 21)
    # Pad to minimum character size (89 bytes)
    template += b"\x00" * (89 - len(template))
    
    common_char_file.write_bytes(char_data + template)

    return {
        "header": header_file,
        "common_char": common_char_file
    }
