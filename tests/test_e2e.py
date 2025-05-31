"""
End-to-end tests for mb-app CLI application.

These tests verify the complete workflow that we demonstrated when testing
the bug fix for issue #9 (character generation sample reuse bug).

The tests cover:
1. Complete workflow: generation, listing, backup, restore, deletion
2. Character data independence verification (bug #9 fix)
3. WSE2 workflow support

These tests ensure that:
- Characters are generated with valid skin values (White, Light, Tan, Dark, Black)
- No corrupted skin values like "Unknown (255)" appear
- Each character has independent data (no sample reuse corruption)
- All CLI operations work together seamlessly
"""

import logging
import pytest
from pathlib import Path

from appearance.app import main


def test_e2e_complete_workflow(tmp_path, monkeypatch, caplog):
    """End-to-end test covering the complete workflow we demonstrated."""
    # Setup test environment
    profiles_dir = tmp_path / "Mount&Blade Warband"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Mock the profiles directory detection
    def mock_get_profiles_file_path(wse2=False):
        return profiles_file
    
    monkeypatch.setattr("appearance.consts.get_profiles_file_path", mock_get_profiles_file_path)
    
    # Mock sys.argv for each command
    def run_command(args):
        monkeypatch.setattr("sys.argv", ["mb-app"] + args)
        with caplog.at_level(logging.INFO):
            main()
    
    # 1. Generate 5 characters
    run_command(["--gen", "5"])
    assert "Successfully generated 5 random characters!" in caplog.text
    caplog.clear()
    
    # 2. List characters and verify they have valid skin values
    run_command(["--list"])
    assert "Characters in profiles.dat:" in caplog.text
    
    # Extract character info from logs
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 5
    
    # Verify all characters have valid skin values (no "Unknown" values)
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for line in character_lines:
        assert any(skin in line for skin in valid_skins), f"Invalid skin in: {line}"
        assert 'Unknown' not in line, f"Corrupted skin value in: {line}"
    
    caplog.clear()
    
    # 3. Generate 15 more characters
    run_command(["--gen", "15"])
    assert "Successfully generated 15 random characters!" in caplog.text
    caplog.clear()
    
    # 4. List all 15 characters and verify no corruption
    run_command(["--list"])
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 15
    
    # Verify all 15 characters have valid skin values
    for line in character_lines:
        assert any(skin in line for skin in valid_skins), f"Invalid skin in: {line}"
        assert 'Unknown' not in line, f"Corrupted skin value in: {line}"
    
    caplog.clear()
    
    # 5. Create a backup
    run_command(["--backup", "test_backup"])
    assert "Successfully made backup to" in caplog.text
    assert "test_backup.dat" in caplog.text
    caplog.clear()
    
    # 6. Show available backups
    run_command(["--show"])
    assert "Available backups:" in caplog.text
    assert "test_backup" in caplog.text
    caplog.clear()
    
    # 7. Generate 3 new characters (overwrite existing)
    run_command(["--gen", "3"])
    assert "Successfully generated 3 random characters!" in caplog.text
    caplog.clear()
    
    # 8. Verify only 3 characters exist now
    run_command(["--list"])
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 3
    caplog.clear()
    
    # 9. Restore from backup
    run_command(["--restore", "test_backup"])
    assert "Successfully restored from backup" in caplog.text
    caplog.clear()
    
    # 10. Verify 15 characters are back
    run_command(["--list"])
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 15
    
    # Store character names for deletion test
    first_char_line = character_lines[0]
    fifth_char_line = character_lines[5] if len(character_lines) > 5 else character_lines[1]
    
    # Extract character name from line like "INFO: 5. g (Female, Tan)"
    char_name_to_delete = fifth_char_line.split('. ')[1].split(' ')[0]
    
    caplog.clear()
    
    # 11. Delete character by index (index 5)
    run_command(["--delete", "5"])
    assert "Successfully deleted character at index 5" in caplog.text
    caplog.clear()
    
    # 12. Verify character was deleted (should have 14 now)
    run_command(["--list"])
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 14
    caplog.clear()
    
    # 13. Delete character by name
    # Find a character name from the current list
    run_command(["--list"])
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    if character_lines:
        # Extract name from first character line
        char_to_delete = character_lines[2].split('. ')[1].split(' ')[0]
        caplog.clear()
        
        run_command(["--delete", char_to_delete])
        assert f"Successfully deleted character '{char_to_delete}'" in caplog.text
        caplog.clear()
        
        # 14. Verify character was deleted (should have 13 now)
        run_command(["--list"])
        character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
        assert len(character_lines) == 13
        
        # Verify the deleted character is no longer in the list
        remaining_chars = [line.split('. ')[1].split(' ')[0] for line in character_lines]
        assert char_to_delete not in remaining_chars


def test_e2e_character_data_independence(stub_profiles_file, stub_resource_files):
    """Test that generated characters have independent data (bug #9 fix verification)."""
    from appearance.service import generate_n_random_characters, list_characters
    
    # Generate a large number of characters to test for corruption
    generate_n_random_characters(
        25,  # Enough to trigger the original bug
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Read the generated file and verify character independence
    characters = list_characters(profiles_file_path=str(stub_profiles_file))
    
    assert len(characters) == 25
    
    # Verify all characters have valid skin values
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for i, char in enumerate(characters):
        assert char['skin'] in valid_skins, f"Character {i} ({char['name']}) has invalid skin: {char['skin']}"
        assert 'Unknown' not in char['skin'], f"Character {i} ({char['name']}) has corrupted skin value"
    
    # Verify we have variation in character attributes (not all identical)
    sex_values = [char['sex'] for char in characters]
    skin_values = [char['skin'] for char in characters]
    
    # With 25 characters and random generation, we should see variation
    assert len(set(sex_values)) > 1, "All characters have identical sex - possible data corruption"
    assert len(set(skin_values)) > 1, "All characters have identical skin - possible data corruption"


def test_e2e_wse2_workflow(tmp_path, monkeypatch, caplog):
    """Test the workflow with WSE2 flag."""
    # Setup test environment for WSE2
    profiles_dir = tmp_path / "Mount&Blade Warband WSE2"
    profiles_dir.mkdir()
    profiles_file = profiles_dir / "profiles.dat"
    
    # Mock the profiles directory detection for WSE2
    def mock_get_profiles_file_path(wse2=False):
        if wse2:
            return profiles_file
        else:
            # Return a different path for non-WSE2
            regular_dir = tmp_path / "Mount&Blade Warband"
            regular_dir.mkdir(exist_ok=True)
            return regular_dir / "profiles.dat"
    
    monkeypatch.setattr("appearance.consts.get_profiles_file_path", mock_get_profiles_file_path)
    
    def run_command(args):
        monkeypatch.setattr("sys.argv", ["mb-app"] + args)
        with caplog.at_level(logging.INFO):
            main()
    
    # Generate characters with WSE2 flag
    run_command(["--gen", "5", "--wse2"])
    assert "Successfully generated 5 random characters!" in caplog.text
    caplog.clear()
    
    # List WSE2 characters
    run_command(["--list", "--wse2"])
    assert "Characters in profiles.dat:" in caplog.text
    
    character_lines = [line for line in caplog.text.split('\n') if '. ' in line and '(' in line]
    assert len(character_lines) == 5
    
    # Verify all WSE2 characters have valid skin values
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for line in character_lines:
        assert any(skin in line for skin in valid_skins), f"Invalid skin in WSE2 character: {line}"
        assert 'Unknown' not in line, f"Corrupted skin value in WSE2 character: {line}"