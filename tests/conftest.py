
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
    header_file.write_bytes(b"\x00" * 16)  # 16 byte header

    # Create a stub common_char file
    common_char_file = tmp_path / "common_char.dat"
    # 12 bytes offset + character data
    common_char_file.write_bytes(b"\x00" * 12 + b"\x00" * 284)

    return {
        "header": header_file,
        "common_char": common_char_file
    }
