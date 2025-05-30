from pathlib import Path

from appearance.consts import ALLOWED_NAME_CHARS


def validate_file_exists(filepath: Path) -> bool:
    return filepath.is_file()


def validate_is_int(num) -> bool:
    try:
        int(num)
    except (ValueError, TypeError):
        return False
    return True


def validate_name(name: str) -> bool:
    if len(name) < 1 or len(name) > 28:
        return False
    return all(ch in ALLOWED_NAME_CHARS for ch in name)


def validate_sex(sex: int) -> bool:
    return sex in {0, 1}


def validate_at_least_one_arg(*args):
    return any(arg is not None for arg in args)
