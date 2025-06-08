import logging
import string
from pathlib import Path

from appearance.consts import (
    APPEARANCE_BYTES_AMOUNT,
    BACKUP_FILE_DIR,
    CHAR_OFFSETS,
    COMMON_CHAR_FILE_PATH,
    HEADER_FILE_PATH,
    MIN_BYTES_AMOUNT_FOR_CHAR,
    get_profiles_file_path,
)
from appearance.helpers import (
    get_header_with_chars_amount,
    get_name_length,
    get_random_byte_for_idx,
    get_random_sex,
    get_random_skin,
    read_profiles,
    write_profiles,
)

logger = logging.getLogger(__name__)


def backup(backup_to_filename: str, wse2: bool = False, profiles_file_path=None, backup_dir=None):
    """Create a backup of the profiles file.

    Args:
        backup_to_filename: Name of the backup file
        wse2: Whether to use WSE2 profiles
        profiles_file_path: Override path to profiles file (for testing)
        backup_dir: Override backup directory (for testing)
    """
    if profiles_file_path is None:
        profiles_file_path = get_profiles_file_path(wse2)
    if backup_dir is None:
        backup_dir = BACKUP_FILE_DIR

    profiles = read_profiles(profiles_file_path)
    backup_path = Path(backup_dir, backup_to_filename)
    write_profiles(backup_path, profiles)
    logger.info("Successfully made backup to %s!", backup_path.resolve())


def show_backuped_characters(backup_dir_path: Path):
    """Show available backup files."""
    logger.info("Available backups:")
    for idx, file in enumerate(Path(backup_dir_path).glob("*.dat"), start=1):
        logger.info("%d. %s", idx, file.name.split(".")[0])


def restore_from_backup(restore_dir_path: Path, restore_from_filename: str, wse2: bool = False, profiles_file_path=None):
    """Restore profiles from a backup file.

    Args:
        restore_dir_path: Directory containing backup files
        restore_from_filename: Name of the backup file to restore
        wse2: Whether to use WSE2 profiles
        profiles_file_path: Override path to profiles file (for testing)
    """
    restore_path = Path(restore_dir_path, restore_from_filename)
    profiles = read_profiles(restore_path)

    if profiles_file_path is None:
        profiles_file_path = get_profiles_file_path(wse2)

    write_profiles(profiles_file_path, profiles)
    logger.info("Successfully restored from backup located at %s!", restore_path.resolve())


def generate_n_random_characters(
    n: int,
    wse2: bool = False,
    profiles_file_path=None,
    header_file_path=None,
    common_char_file_path=None
):
    """Generate n random characters.

    Args:
        n: Number of characters to generate
        wse2: Whether to use WSE2 profiles
        profiles_file_path: Override path to profiles file (for testing)
        header_file_path: Override path to header file (for testing)
        common_char_file_path: Override path to common char file (for testing)
    """
    if header_file_path is None:
        header_file_path = HEADER_FILE_PATH
    if common_char_file_path is None:
        common_char_file_path = COMMON_CHAR_FILE_PATH

    header = read_profiles(header_file_path)
    header = get_header_with_chars_amount(header, n)
    sample = read_profiles(common_char_file_path)[12:]

    appearance_offset = CHAR_OFFSETS["APPEARANCE"]
    name_offset = CHAR_OFFSETS["NAME"]
    sex_offset = CHAR_OFFSETS["SEX"]
    skin_offset = CHAR_OFFSETS["SKIN"]

    names = string.ascii_lowercase

    for char_idx in range(n):
        # Create a fresh copy of the template for each character
        char_data = sample[:]
        
        for i in range(APPEARANCE_BYTES_AMOUNT):
            rb = get_random_byte_for_idx(i)
            # random appearance
            char_data = char_data[0:appearance_offset + i] + rb + char_data[appearance_offset + i + 1:]
        
        # random sex
        char_data = char_data[0:sex_offset] + get_random_sex() + char_data[sex_offset + 1:]
        # random skin
        char_data = char_data[0:skin_offset] + get_random_skin() + char_data[skin_offset + 1:]
        # set name with numbering strategy
        letter_idx = char_idx % len(names)
        group_number = char_idx // len(names)
        if group_number == 0:
            name = names[letter_idx]
        else:
            name = names[letter_idx] + str(group_number)
        name_bytes = name.encode()
        name_length = len(name_bytes)
        # Update name length at offset 0
        char_data = bytes([name_length]) + char_data[1:]
        # Update name at offset 4
        char_data = char_data[0:name_offset] + name_bytes + char_data[name_offset + name_length:]
        header += char_data

    if profiles_file_path is None:
        profiles_file_path = get_profiles_file_path(wse2)

    write_profiles(profiles_file_path, header)
    logger.info("Successfully generated %d random characters in %s!", n, profiles_file_path)


def list_characters(profiles_file_path: str = None, wse2: bool = False) -> list:
    """List all characters in the profiles file.
    
    Args:
        profiles_file_path: Override path to profiles file (for testing)
        wse2: Whether to use WSE2 profiles
        
    Returns:
        List of dictionaries containing character information
    """
    if profiles_file_path is None:
        profiles_file_path = get_profiles_file_path(wse2)
    
    try:
        # Read the entire profiles file
        profiles_data = read_profiles(profiles_file_path)
        
        # Extract header and character count
        # Read both count fields to handle corruption
        char_count1 = int.from_bytes(profiles_data[4:8], 'little')
        char_count2 = int.from_bytes(profiles_data[8:12], 'little')
        
        # Use the larger count if they differ (handles corruption)
        if char_count1 != char_count2:
            logger.warning(f"Character count mismatch: offset 4-7={char_count1}, offset 8-11={char_count2}. Using larger value.")
            char_count = max(char_count1, char_count2)
        else:
            char_count = char_count1
        
        # Parse all characters
        characters = []
        current_pos = 12  # Start after header
        
        for i in range(char_count):
            if current_pos >= len(profiles_data):
                break
                
            char_info = {}
            char_info['index'] = i
            
            # Get name length (at offset 0 of character)
            name_length = profiles_data[current_pos]
            
            # Get character name
            name_start = current_pos + 4
            name_end = name_start + name_length
            char_info['name'] = profiles_data[name_start:name_end].decode('utf-8', errors='ignore').rstrip('\x00')
            
            # Get character sex (0=male, 1=female)
            # Sex is at offset 5 from character start
            sex_offset = current_pos + CHAR_OFFSETS["SEX"]
            sex_byte = profiles_data[sex_offset]
            char_info['sex'] = 'Female' if sex_byte == 1 else 'Male'
            
            # Get character skin
            # Skin is at offset 14 from character start
            skin_offset = current_pos + CHAR_OFFSETS["SKIN"]
            skin_byte = profiles_data[skin_offset]
            skin_map = {0: 'White', 16: 'Light', 32: 'Tan', 48: 'Dark', 64: 'Black'}
            char_info['skin'] = skin_map.get(skin_byte, f'Unknown ({skin_byte})')
            
            # Get Age, Hair style, and Hair color using fixed offsets
            # Based on reverse-engineered format documentation and binary analysis
            
            # Age (2 bytes, little endian) at offset 15
            age_offset = current_pos + CHAR_OFFSETS["AGE"]
            if age_offset + 1 < len(profiles_data):
                age_bytes = profiles_data[age_offset:age_offset + 2]
                if len(age_bytes) == 2:
                    char_info['age'] = int.from_bytes(age_bytes, 'little')
            
            # Hair style (1 byte) at offset 17
            hair_offset = current_pos + CHAR_OFFSETS["HAIRSTYLE"]
            if hair_offset < len(profiles_data):
                char_info['hairstyle'] = str(profiles_data[hair_offset])
            
            # Hair color (1 byte) at offset 18
            hair_color_offset = current_pos + CHAR_OFFSETS["HAIR_COLOR"]
            if hair_color_offset < len(profiles_data):
                char_info['hair_color'] = str(profiles_data[hair_color_offset])
            
            # Get banner data (4 bytes at offset 9)
            banner_offset = current_pos + CHAR_OFFSETS["BANNER"]
            banner_bytes = profiles_data[banner_offset:banner_offset + 4]
            if len(banner_bytes) >= 4:
                if banner_bytes == b'\xFF\xFF\xFF\xFF':
                    char_info['banner'] = "Current Nation"
                else:
                    banner_value = int.from_bytes(banner_bytes, 'little')
                    char_info['banner'] = f"{banner_value:08X}"
            
            # Calculate character size
            char_size = 4 + name_length + (85 - name_length)
            if char_size < MIN_BYTES_AMOUNT_FOR_CHAR:
                char_size = MIN_BYTES_AMOUNT_FOR_CHAR
            
            characters.append(char_info)
            current_pos += char_size
        
        return characters
        
    except Exception as e:
        logger.error("Failed to list characters: %s", str(e))
        return []


def delete_character(profiles_file_path: str, index: int = None, name: str = None) -> bool:
    """Delete a character from the profiles file.
    
    Args:
        profiles_file_path: Path to the profiles.dat file
        index: Character index to delete (0-based)
        name: Character name to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    # Must specify either index or name
    if index is None and name is None:
        logger.error("Must specify either index or name to delete")
        return False
    
    try:
        # Read the entire profiles file
        profiles_data = read_profiles(profiles_file_path)
        
        # Extract header and character count
        header = profiles_data[:12]
        char_count = int.from_bytes(profiles_data[4:8], 'little')
        
        # Don't allow deleting the last character
        if char_count <= 1:
            logger.error("Cannot delete the last remaining character")
            return False
        
        # Find all character positions
        char_positions = []
        current_pos = 12  # Start after header
        
        for i in range(char_count):
            if current_pos >= len(profiles_data):
                break
                
            char_start = current_pos
            
            # Get name length (at offset 0 of character)
            name_length = profiles_data[current_pos]
            
            # Calculate character size
            # Structure: name_length(1) + padding(3) + name(variable) + rest(85-name_length)
            char_size = 4 + name_length + (85 - name_length)
            
            # Ensure minimum size
            if char_size < MIN_BYTES_AMOUNT_FOR_CHAR:
                char_size = MIN_BYTES_AMOUNT_FOR_CHAR
            
            char_positions.append({
                'index': i,
                'start': char_start,
                'end': char_start + char_size,
                'name_start': char_start + 4,
                'name_end': char_start + 4 + name_length,
                'size': char_size
            })
            
            current_pos += char_size
        
        # Find the character to delete
        char_to_delete = None
        
        if index is not None:
            # Delete by index (index takes precedence)
            if 0 <= index < len(char_positions):
                char_to_delete = char_positions[index]
            else:
                logger.error("Invalid character index: %d", index)
                return False
        elif name is not None:
            # Delete by name
            for char_info in char_positions:
                char_name = profiles_data[char_info['name_start']:char_info['name_end']].decode('utf-8', errors='ignore').rstrip('\x00')
                if char_name == name:
                    char_to_delete = char_info
                    break
            
            if char_to_delete is None:
                logger.error("Character with name '%s' not found", name)
                return False
        
        # Delete the character by removing its bytes
        new_data = profiles_data[:char_to_delete['start']] + profiles_data[char_to_delete['end']:]
        
        # Update character count in header
        new_count = char_count - 1
        new_header = get_header_with_chars_amount(header, new_count)
        new_data = new_header + new_data[12:]
        
        # Write the modified data back
        write_profiles(profiles_file_path, new_data)
        
        if index is not None:
            logger.info("Successfully deleted character at index %d", index)
        else:
            logger.info("Successfully deleted character '%s'", name)
        
        return True
        
    except Exception as e:
        logger.error("Failed to delete character: %s", str(e))
        return False
