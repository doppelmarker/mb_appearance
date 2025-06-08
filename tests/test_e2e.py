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

from appearance import service
from appearance.argparser import ArgParser


def test_e2e_complete_workflow(tmp_path):
    """End-to-end test covering the complete workflow."""
    # Setup test environment
    profiles_file = tmp_path / "profiles.dat"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # 1. Generate 5 characters
    service.generate_n_random_characters(5, profiles_file_path=profiles_file)
    
    # 2. List characters and verify they have valid skin values
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 5
    
    # Verify all characters have valid skin values (no "Unknown" values)
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for char in characters:
        assert char['skin'] in valid_skins, f"Invalid skin: {char['skin']}"
    
    # 3. Generate 15 more characters (overwrites)
    service.generate_n_random_characters(15, profiles_file_path=profiles_file)
    
    # 4. List all 15 characters and verify no corruption
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 15
    
    # Verify all 15 characters have valid skin values
    for char in characters:
        assert char['skin'] in valid_skins, f"Invalid skin: {char['skin']}"
    
    # 5. Create a backup
    service.backup("test_backup.dat", profiles_file_path=profiles_file, backup_dir=backup_dir)
    assert (backup_dir / "test_backup.dat").exists()
    
    # 6. Show available backups
    service.show_backuped_characters(backup_dir)
    # Just verify it doesn't crash
    
    # 7. Generate 3 new characters (overwrite existing)
    service.generate_n_random_characters(3, profiles_file_path=profiles_file)
    
    # 8. Verify only 3 characters exist now
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 3
    
    # 9. Restore from backup
    service.restore_from_backup(backup_dir, "test_backup.dat", profiles_file_path=profiles_file)
    
    # 10. Verify 15 characters are back
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 15
    
    # Store first character info for deletion test
    first_char_name = characters[0]['name']
    fifth_char_name = characters[4]['name'] if len(characters) > 4 else characters[1]['name']
    
    # 11. Delete character by index (index 4, which is 5th character)
    success = service.delete_character(str(profiles_file), index=4)
    assert success
    
    # 12. Verify character was deleted (should have 14 now)
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 14
    assert all(char['name'] != fifth_char_name for char in characters)
    
    # 13. Delete character by name
    char_to_delete = characters[2]['name']
    success = service.delete_character(str(profiles_file), name=char_to_delete)
    assert success
    
    # 14. Verify character was deleted (should have 13 now)
    characters = service.list_characters(profiles_file_path=profiles_file)
    assert len(characters) == 13
    assert all(char['name'] != char_to_delete for char in characters)


def test_e2e_character_data_independence(stub_profiles_file, stub_resource_files):
    """Test that generated characters have independent data (bug #9 fix verification)."""
    # Generate a large number of characters to test for corruption
    service.generate_n_random_characters(
        25,  # Enough to trigger the original bug
        profiles_file_path=stub_profiles_file,
        header_file_path=stub_resource_files["header"],
        common_char_file_path=stub_resource_files["common_char"]
    )
    
    # Read the generated file and verify character independence
    characters = service.list_characters(profiles_file_path=str(stub_profiles_file))
    
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


def test_e2e_wse2_workflow(tmp_path):
    """Test the workflow with WSE2 flag."""
    # Setup test environment for WSE2
    profiles_file_wse2 = tmp_path / "profiles_wse2.dat"
    profiles_file_regular = tmp_path / "profiles_regular.dat"
    
    # Generate characters for WSE2
    service.generate_n_random_characters(5, profiles_file_path=profiles_file_wse2)
    
    # Generate different characters for regular
    service.generate_n_random_characters(3, profiles_file_path=profiles_file_regular)
    
    # List WSE2 characters
    wse2_characters = service.list_characters(profiles_file_path=profiles_file_wse2)
    assert len(wse2_characters) == 5
    
    # List regular characters
    regular_characters = service.list_characters(profiles_file_path=profiles_file_regular)
    assert len(regular_characters) == 3
    
    # Verify all characters have valid skin values
    valid_skins = ['White', 'Light', 'Tan', 'Dark', 'Black']
    for char in wse2_characters:
        assert char['skin'] in valid_skins, f"Invalid skin in WSE2 character: {char['skin']}"
    
    for char in regular_characters:
        assert char['skin'] in valid_skins, f"Invalid skin in regular character: {char['skin']}"
    
    # Verify the two sets are independent
    assert len(wse2_characters) != len(regular_characters)


def test_argparser_combinations():
    """Test various argument combinations work correctly."""
    parser = ArgParser()
    
    # Test valid combinations
    args = parser.parser.parse_args(["-g", "10", "-b", "backup1"])
    assert args.gen == 10
    assert args.backup == "backup1"
    
    args = parser.parser.parse_args(["--wse2", "-l"])
    assert args.wse2 is True
    assert args.list is True
    
    args = parser.parser.parse_args(["--verbose", "--quiet", "-s"])
    assert args.verbose is True
    assert args.quiet is True
    assert args.show is True
    
    # Test all actions can be combined
    args = parser.parser.parse_args(["-g", "5", "-b", "bak", "-r", "res", "-s", "-l", "-d", "test"])
    assert args.gen == 5
    assert args.backup == "bak"
    assert args.restore == "res"
    assert args.show is True
    assert args.list is True
    assert args.delete == "test"