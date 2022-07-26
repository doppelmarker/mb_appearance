from pathlib import Path

from appearance.consts import ALLOWED_NAME_CHARS


def validate_file_exists(filepath: Path) -> bool:
    return True if filepath.is_file() else False


def validate_is_int(num) -> bool:
    try:
        int(num)
    except ValueError:
        return False
    return True


def validate_name(name: str) -> bool:
    if len(name) < 1 or len(name) > 28:
        return False
    for ch in name:
        if ch not in ALLOWED_NAME_CHARS:
            return False
    return True


def validate_sex(sex: int) -> bool:
    if sex != 0 and sex != 1:
        return False
    return True


def validate_at_least_one_arg(*args):
    for arg in args:
        if arg is not None:
            return True
    return False
