import string
import sys
from pathlib import Path


def get_profiles_dir_path(wse2: bool = False, platform: str = None, home_path: Path = None) -> Path:
    """Get the profiles directory path based on platform.
    
    Args:
        wse2: Whether to use WSE2 directory
        platform: Platform string (defaults to sys.platform)
        home_path: Home directory path (defaults to Path.home())
    """
    if platform is None:
        platform = sys.platform
    if home_path is None:
        home_path = Path.home()
    
    home = home_path
    mb_dir_name = "Mount&Blade Warband WSE2" if wse2 else "Mount&Blade Warband"

    if platform == "win32":
        return home / "AppData/Roaming" / mb_dir_name
    if platform == "linux":
        return home / ".local/share" / mb_dir_name
    if platform == "darwin":
        return home / "Library/Application Support" / mb_dir_name
    return home / mb_dir_name  # Fallback for unknown platforms


def get_profiles_file_path(wse2: bool = False, platform: str = None, home_path: Path = None) -> Path:
    """Get the profiles.dat file path.
    
    Args:
        wse2: Whether to use WSE2 directory
        platform: Platform string (defaults to sys.platform)
        home_path: Home directory path (defaults to Path.home())
    """
    return get_profiles_dir_path(wse2, platform, home_path) / PROFILES_FILE_NAME


PROFILES_DIR_PATH = get_profiles_dir_path()
PROFILES_FILE_NAME = "profiles.dat"
PROFILES_FILE_PATH = Path(PROFILES_DIR_PATH, PROFILES_FILE_NAME)

RESOURCES_FILE_DIR = Path(Path(__file__).parent, "../resources")
HEADER_FILE_PATH = Path(RESOURCES_FILE_DIR, "header.dat")
COMMON_CHAR_FILE_PATH = Path(RESOURCES_FILE_DIR, "common_char.dat")

BACKUP_FILE_DIR = Path(RESOURCES_FILE_DIR, "backups")

HEADER_OFFSETS = {
    "CHAR_AMOUNT1": 4,
    "CHAR_AMOUNT2": 8,
}

CHAR_OFFSETS = {
    "NAME_LENGTH": 0,
    "NAME": 4,
    "SEX": 5,
    "BANNER": 9,
    "SKIN": 14,
    "AGE": 15,           # 2 bytes, little endian
    "HAIRSTYLE": 17,     # 1 byte
    "HAIR_COLOR": 18,    # 1 byte
    "APPEARANCE": 21,    # Random appearance bytes (legacy)
}

BANNER_BYTES_AMOUNT = 4
APPEARANCE_BYTES_AMOUNT = 11

MIN_BYTES_AMOUNT_FOR_CHAR = 89

ALLOWED_NAME_CHARS = "_-*[]~" + string.ascii_letters + "0123456789"

# file size of the max number of lightest characters is about 364 GB, 100000 characters - 8,48 MB
MAX_CHARS_AMOUNT = 42949672964294967295
# the maximum number of in-game displayed characters
MAX_CHARS_IN_GAME_DISPLAYED = 22
