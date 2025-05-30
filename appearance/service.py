import logging
import string
from pathlib import Path

from appearance.consts import (
    APPEARANCE_BYTES_AMOUNT,
    BACKUP_FILE_DIR,
    CHAR_OFFSETS,
    COMMON_CHAR_FILE_PATH,
    HEADER_FILE_PATH,
    get_profiles_file_path,
)
from appearance.helpers import (
    get_header_with_chars_amount,
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
        for i in range(APPEARANCE_BYTES_AMOUNT):
            rb = get_random_byte_for_idx(i)
            # random sex
            sample = sample[0:sex_offset] + get_random_sex() + sample[sex_offset + 1:]
            # random skin
            sample = sample[0:skin_offset] + get_random_skin() + sample[skin_offset + 1:]
            # random appearance
            sample = sample[0:appearance_offset + i] + rb + sample[appearance_offset + i + 1:]
        # set name
        sample = sample[0:name_offset] + names[char_idx % len(names)].encode() + sample[name_offset + 1:]
        header += sample

    if profiles_file_path is None:
        profiles_file_path = get_profiles_file_path(wse2)

    write_profiles(profiles_file_path, header)
    logger.info("Successfully generated %d random characters!", n)
