import string
from pathlib import Path

from appearance.consts import get_profiles_file_path, BACKUP_FILE_DIR, HEADER_FILE_PATH, \
    COMMON_CHAR_FILE_PATH, CHAR_OFFSETS, APPEARANCE_BYTES_AMOUNT
from appearance.helpers import read_profiles, write_profiles, \
    get_header_with_chars_amount, get_random_byte_for_idx, get_random_sex, get_random_skin


def backup(backup_to_filename: str, wse2: bool = False):
    profiles_file_path = get_profiles_file_path(wse2)
    profiles = read_profiles(profiles_file_path)
    backup_path = Path(BACKUP_FILE_DIR, backup_to_filename)
    write_profiles(backup_path, profiles)
    print(f'Successfully made backup to {backup_path.resolve()}!')


def show_backuped_characters(backup_dir_path: Path):
    print("Available backups:")
    for idx, file in enumerate(Path(backup_dir_path).glob("*.dat"), start=1):
        print(f"{idx}. {file.name.split('.')[0]}")


def restore_from_backup(restore_dir_path: Path, restore_from_filename: str, wse2: bool = False):
    restore_path = Path(restore_dir_path, restore_from_filename)
    profiles = read_profiles(restore_path)
    profiles_file_path = get_profiles_file_path(wse2)
    write_profiles(profiles_file_path, profiles)
    print(f'Successfully restored from backup located at {restore_path.resolve()}!')


def generate_n_random_characters(n: int, wse2: bool = False):
    header = read_profiles(HEADER_FILE_PATH)
    header = get_header_with_chars_amount(header, n)
    sample = read_profiles(COMMON_CHAR_FILE_PATH)[12:]

    appearance_offset = CHAR_OFFSETS['APPEARANCE']
    name_offset = CHAR_OFFSETS['NAME']
    sex_offset = CHAR_OFFSETS['SEX']
    skin_offset = CHAR_OFFSETS['SKIN']

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

    profiles_file_path = get_profiles_file_path(wse2)
    write_profiles(profiles_file_path, header)
    print(f'Successfully generated {n} random characters!')
