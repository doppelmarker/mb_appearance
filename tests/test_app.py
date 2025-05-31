import logging
import sys
from io import StringIO
from pathlib import Path

import pytest

from appearance.app import main


def test_main_with_show_command(stub_backup_dir, monkeypatch, caplog):
    # Create backup files
    (stub_backup_dir / "backup1.dat").write_bytes(b"data1")
    
    # Monkeypatch the constants
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", stub_backup_dir)
    
    # Mock command line arguments
    test_args = ["mb-app", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    assert "Available backups:" in caplog.text
    assert "backup1" in caplog.text


def test_main_with_backup_command(tmp_path, monkeypatch):
    # Create test directories
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"test profile data")
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.service.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-b", "test_backup"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    main()
    
    # Verify backup was created
    backup_file = backup_dir / "test_backup.dat"
    assert backup_file.exists()
    assert backup_file.read_bytes() == b"test profile data"


def test_main_with_backup_command_adds_dat_extension(tmp_path, monkeypatch):
    # Create test directories
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"test profile data")
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.service.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments with .txt extension
    test_args = ["mb-app", "-b", "test_backup.txt"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    main()
    
    # Verify backup was created with .dat extension
    backup_file = backup_dir / "test_backup.dat"
    assert backup_file.exists()
    assert not (backup_dir / "test_backup.txt").exists()


def test_main_with_restore_command_from_backup(tmp_path, monkeypatch):
    # Create backup directory with backup file
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup_file = backup_dir / "test_restore.dat"
    backup_data = b"backup profile data"
    backup_file.write_bytes(backup_data)
    
    # Create profiles directory
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"old data")
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-r", "test_restore", "--wse2"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    main()
    
    # Verify profile was restored
    assert profiles_file.read_bytes() == backup_data


def test_main_with_restore_command_from_resources(tmp_path, monkeypatch):
    # Create directories
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    
    # Create resource file (backup doesn't exist)
    resource_file = resources_dir / "test_restore.dat"
    resource_data = b"resource profile data"
    resource_file.write_bytes(resource_data)
    
    # Create profiles directory
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    profiles_file.write_bytes(b"old data")
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.app.RESOURCES_FILE_DIR", resources_dir)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-r", "test_restore.dat"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    main()
    
    # Verify profile was restored from resources
    assert profiles_file.read_bytes() == resource_data


def test_main_with_restore_command_file_not_found(tmp_path, monkeypatch, capsys):
    # Create empty directories
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.BACKUP_FILE_DIR", backup_dir)
    monkeypatch.setattr("appearance.app.RESOURCES_FILE_DIR", resources_dir)
    
    # Mock command line arguments
    test_args = ["mb-app", "-r", "nonexistent"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Malformed restore path!" in captured.err


def test_main_with_generate_command(tmp_path, monkeypatch):
    # Create test directories and files
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    header_file = resources_dir / "header.dat"
    header_file.write_bytes(b"\x00" * 16)
    common_char_file = resources_dir / "common_char.dat"
    common_char_file.write_bytes(b"\x00" * 12 + b"\x00" * 284)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.HEADER_FILE_PATH", header_file)
    monkeypatch.setattr("appearance.service.COMMON_CHAR_FILE_PATH", common_char_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-g", "10"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    main()
    
    # Verify profiles file was created
    assert profiles_file.exists()
    content = profiles_file.read_bytes()
    assert len(content) > 16  # Has header + characters


def test_main_with_no_action(monkeypatch, capsys):
    # Mock command line arguments with no action
    test_args = ["mb-app"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "No action requested!" in captured.err


def test_main_with_verbose_logging(tmp_path, monkeypatch, caplog):
    # Create test directories
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    header_file = resources_dir / "header.dat"
    header_file.write_bytes(b"\x00" * 16)
    common_char_file = resources_dir / "common_char.dat"
    common_char_file.write_bytes(b"\x00" * 12 + b"\x00" * 284)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.HEADER_FILE_PATH", header_file)
    monkeypatch.setattr("appearance.service.COMMON_CHAR_FILE_PATH", common_char_file)
    
    # Mock command line arguments with verbose flag
    test_args = ["mb-app", "-g", "1", "--verbose"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Capture all logs including DEBUG
    with caplog.at_level(logging.DEBUG):
        main()
    
    # Should have INFO message
    assert "Successfully generated 1 random characters!" in caplog.text


def test_main_with_quiet_logging(tmp_path, monkeypatch, caplog):
    # Create test directories
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    header_file = resources_dir / "header.dat"
    header_file.write_bytes(b"\x00" * 16)
    common_char_file = resources_dir / "common_char.dat"
    common_char_file.write_bytes(b"\x00" * 12 + b"\x00" * 284)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.HEADER_FILE_PATH", header_file)
    monkeypatch.setattr("appearance.service.COMMON_CHAR_FILE_PATH", common_char_file)
    
    # Mock command line arguments with quiet flag
    test_args = ["mb-app", "-g", "1", "--quiet"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Capture logs starting from ERROR (quiet should suppress INFO)
    with caplog.at_level(logging.ERROR):
        main()
    
    # Should not have any ERROR messages for successful operation
    assert len(caplog.records) == 0


def test_main_with_default_logging(tmp_path, monkeypatch, caplog):
    # Create test directories
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    header_file = resources_dir / "header.dat"
    header_file.write_bytes(b"\x00" * 16)
    common_char_file = resources_dir / "common_char.dat"
    common_char_file.write_bytes(b"\x00" * 12 + b"\x00" * 284)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.HEADER_FILE_PATH", header_file)
    monkeypatch.setattr("appearance.service.COMMON_CHAR_FILE_PATH", common_char_file)
    
    # Mock command line arguments without verbose or quiet
    test_args = ["mb-app", "-g", "1"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Capture logs at INFO level
    with caplog.at_level(logging.INFO):
        main()
    
    # Should have INFO message
    assert "Successfully generated 1 random characters!" in caplog.text


def test_main_with_delete_command_by_index(tmp_path, monkeypatch, caplog):
    # Create test profiles file with characters
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Create a test file with 3 characters
    header = b'\x0a\x00\x00\x00' + b'\x03\x00\x00\x00' + b'\x03\x00\x00\x00'
    char1 = b'\x09' + b'\x00' * 3 + b'TestChar1' + b'\x00' * 76
    char2 = b'\x09' + b'\x00' * 3 + b'TestChar2' + b'\x00' * 76
    char3 = b'\x09' + b'\x00' * 3 + b'TestChar3' + b'\x00' * 76
    profiles_file.write_bytes(header + char1 + char2 + char3)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-d", "1"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    # Check success message
    assert "Successfully deleted character at index 1" in caplog.text
    
    # Verify character was actually deleted
    data = profiles_file.read_bytes()
    assert b'TestChar1' in data
    assert b'TestChar2' not in data
    assert b'TestChar3' in data


def test_main_with_delete_command_by_name(tmp_path, monkeypatch, caplog):
    # Create test profiles file with characters
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Create a test file with 3 characters
    header = b'\x0a\x00\x00\x00' + b'\x03\x00\x00\x00' + b'\x03\x00\x00\x00'
    char1 = b'\x09' + b'\x00' * 3 + b'TestChar1' + b'\x00' * 76
    char2 = b'\x09' + b'\x00' * 3 + b'TestChar2' + b'\x00' * 76
    char3 = b'\x09' + b'\x00' * 3 + b'TestChar3' + b'\x00' * 76
    profiles_file.write_bytes(header + char1 + char2 + char3)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-d", "TestChar2"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    # Check success message
    assert "Successfully deleted character 'TestChar2'" in caplog.text
    
    # Verify character was actually deleted
    data = profiles_file.read_bytes()
    assert b'TestChar1' in data
    assert b'TestChar2' not in data
    assert b'TestChar3' in data


def test_main_with_delete_command_failure(tmp_path, monkeypatch, capsys):
    # Create test profiles file with only one character
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Create a test file with 1 character
    header = b'\x0a\x00\x00\x00' + b'\x01\x00\x00\x00' + b'\x01\x00\x00\x00'
    char1 = b'\x09' + b'\x00' * 3 + b'TestChar1' + b'\x00' * 76
    profiles_file.write_bytes(header + char1)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-d", "0"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Failed to delete character!" in captured.err


def test_main_with_list_command(tmp_path, monkeypatch, caplog, stub_resource_files):
    # Create test profiles file using actual generation to ensure proper format
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Generate real characters using our fixed generation function
    from appearance.service import generate_n_random_characters
    generate_n_random_characters(
        3,
        profiles_file_path=profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-l"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    # Check output contains all characters with valid skin values
    assert "Characters in profiles.dat:" in caplog.text
    
    # Extract character lines
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 3
    
    # Verify all characters have valid skin values (the key fix verification)
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for line in character_lines:
        assert any(skin in line for skin in valid_skins), f"Invalid skin in: {line}"
        assert 'Unknown' not in line, f"Corrupted skin value in: {line}"


def test_main_with_list_command_no_characters(tmp_path, monkeypatch, caplog):
    # Create test profiles file with no characters
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Create header with 0 characters
    header = b"\x00\x00\x00\x00"  # 4 bytes
    header += b"\x00\x00\x00\x00"  # Character count = 0
    header += b"\x00\x00\x00\x00"  # 4 more bytes
    
    profiles_file.write_bytes(header)
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments
    test_args = ["mb-app", "-l"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    # Should indicate no characters found
    assert "No characters found or unable to read profiles file." in caplog.text


def test_main_with_list_command_wse2(tmp_path, monkeypatch, caplog, stub_resource_files):
    # Create test profiles file for WSE2 using actual generation
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Generate real characters using our fixed generation function
    from appearance.service import generate_n_random_characters
    generate_n_random_characters(
        1,
        profiles_file_path=profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Monkeypatch the paths
    monkeypatch.setattr("appearance.app.get_profiles_file_path", lambda wse2: profiles_file)
    monkeypatch.setattr("appearance.service.get_profiles_file_path", lambda wse2: profiles_file)
    
    # Mock command line arguments with WSE2 flag
    test_args = ["mb-app", "-l", "--wse2"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with caplog.at_level(logging.INFO):
        main()
    
    # Check output contains the character with valid skin value
    assert "Characters in profiles.dat:" in caplog.text
    
    # Extract character lines
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 1
    
    # Verify character has valid skin value
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    line = character_lines[0]
    assert any(skin in line for skin in valid_skins), f"Invalid skin in WSE2 character: {line}"
    assert 'Unknown' not in line, f"Corrupted skin value in WSE2 character: {line}"