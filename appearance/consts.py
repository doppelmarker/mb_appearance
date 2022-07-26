import string
import sys
from pathlib import Path


def get_profiles_dir_path() -> Path:
    home = Path.home()
    mb_dir_name = "Mount&Blade Warband"

    if sys.platform == "win32":
        return home / "AppData/Roaming" / mb_dir_name
    elif sys.platform == "linux":
        return home / ".local/share" / mb_dir_name
    elif sys.platform == "darwin":
        return home / "Library/Application Support" / mb_dir_name


PROFILES_DIR_PATH = get_profiles_dir_path()
PROFILES_FILE_NAME = 'profiles.dat'
PROFILES_FILE_PATH = Path(PROFILES_DIR_PATH, PROFILES_FILE_NAME)

RESOURCES_FILE_DIR = Path('../resources')
HEADER_FILE_PATH = Path(RESOURCES_FILE_DIR, 'header.dat')
COMMON_CHAR_FILE_PATH = Path(RESOURCES_FILE_DIR, 'common_char.dat')

BACKUP_FILE_DIR = Path(RESOURCES_FILE_DIR, 'backups')

HEADER_OFFSETS = {
    'CHAR_AMOUNT1': 4,
    'CHAR_AMOUNT2': 8,
}

CHAR_OFFSETS = {
    'NAME_LENGTH': 0,
    'NAME': 4,
    'SEX': 5,
    'BANNER': 9,
    'SKIN': 14,
    'APPEARANCE': 21,
}

BANNER_BYTES_AMOUNT = 4
APPEARANCE_BYTES_AMOUNT = 11

MIN_BYTES_AMOUNT_FOR_CHAR = 89

ALLOWED_NAME_CHARS = '_-*[]~' + string.ascii_letters + '0123456789'

# file size of the max number of lightest characters is about 364 GB, 100000 characters - 8,48 MB
MAX_CHARS_AMOUNT = 42949672964294967295
# the maximum number of in-game displayed characters
MAX_CHARS_IN_GAME_DISPLAYED = 22
