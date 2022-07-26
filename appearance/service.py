import string
from pathlib import Path

from appearance.consts import PROFILES_FILE_PATH, BACKUP_FILE_DIR, HEADER_FILE_PATH, \
    COMMON_CHAR_FILE_PATH, CHAR_OFFSETS, APPEARANCE_BYTES_AMOUNT
from appearance.helpers import read_profiles, write_profiles, \
    get_header_with_chars_amount, get_random_byte_for_idx, get_random_sex, get_random_skin


def backup(backup_to_filename: str):
    profiles = read_profiles(PROFILES_FILE_PATH)
    backup_path = Path(BACKUP_FILE_DIR, backup_to_filename)
    write_profiles(backup_path, profiles)
    print(f'Successfully made backup to {backup_path.resolve()}!')


def restore_from_backup(restore_dir_path: Path, restore_from_filename: str):
    restore_path = Path(restore_dir_path, restore_from_filename)
    profiles = read_profiles(restore_path)
    write_profiles(PROFILES_FILE_PATH, profiles)
    print(f'Successfully restored from backup located at {restore_path.resolve()}!')


def generate_n_random_characters(n: int):
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

    write_profiles(PROFILES_FILE_PATH, header)
    print(f'Successfully generated {n} random characters!')
