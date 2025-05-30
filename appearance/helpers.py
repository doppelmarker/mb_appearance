import random
from pathlib import Path

from appearance.consts import HEADER_OFFSETS


def int_to_hex_bytes(num: int) -> bytes:
    if num < 0 or num >= 1 << 32:
        raise ValueError("Number should be from 0 to 4294967295")
    length = 1
    if num < 1 << 8:
        length = 1
    elif num < 1 << 16:
        length = 2
    elif num < 1 << 24:
        length = 3
    elif num < 1 << 32:
        length = 4
    return num.to_bytes(length, byteorder="little")


def read_profiles(filepath: Path) -> bytes:
    with open(filepath, mode="rb") as file:
        return file.read()


def write_profiles(filepath: Path, profiles: bytes) -> None:
    # Ensure parent directory exists
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, mode="wb") as file:
        file.write(profiles)


def get_name_length(filepath: Path, offset: int) -> int:
    with open(filepath, mode="rb") as file:
        file.seek(offset, 0)
        ctr = 0
        while True:
            b = file.read(1)
            if not b or b in {b"\x00", b"\x01"}:
                break
            ctr += 1
        return ctr


def get_header_with_chars_amount(header: bytes, amount: int) -> bytes:
    char_amount1_offset = HEADER_OFFSETS["CHAR_AMOUNT1"]
    char_amount2_offset = HEADER_OFFSETS["CHAR_AMOUNT2"]
    hex_bytes_amount = int_to_hex_bytes(amount)
    header = header[0:char_amount1_offset] + hex_bytes_amount + header[char_amount1_offset + len(hex_bytes_amount):]
    return header[0:char_amount2_offset] + hex_bytes_amount + header[char_amount2_offset + len(hex_bytes_amount):]


def get_random_byte_for_idx(idx: int) -> bytes:
    if idx in (0, 1, 2, 3, 4, 5, 6, 8, 9):
        return random.randbytes(1)
    if idx == 7:
        return get_random_byte_between(0, 127)
    return get_random_byte_between(28, 31)


def get_random_byte_between(left: int, right: int) -> bytes:
    return chr(random.randint(left, right)).encode()


def get_random_sex() -> bytes:
    return random.choice((b"\x00", b"\x01"))


def get_random_skin() -> bytes:
    return random.choice((b"\x00", b"\x10", b"\x20", b"\x30", b"\x40"))
