

from appearance.validators import (
    validate_at_least_one_arg,
    validate_file_exists,
    validate_is_int,
    validate_name,
    validate_sex,
)


def test_validate_file_exists_with_existing_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    assert validate_file_exists(test_file) is True


def test_validate_file_exists_with_nonexistent_file(tmp_path):
    test_file = tmp_path / "nonexistent.txt"

    assert validate_file_exists(test_file) is False


def test_validate_file_exists_with_directory(tmp_path):
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    assert validate_file_exists(test_dir) is False


def test_validate_is_int_with_valid_integers():
    assert validate_is_int(0) is True
    assert validate_is_int(123) is True
    assert validate_is_int(-456) is True
    assert validate_is_int("789") is True
    assert validate_is_int("-100") is True


def test_validate_is_int_with_invalid_values():
    assert validate_is_int("abc") is False
    assert validate_is_int("12.34") is False
    assert validate_is_int("") is False
    assert validate_is_int("123abc") is False
    # None and [] will raise TypeError in int(), so they return False
    assert validate_is_int(None) is False
    assert validate_is_int([]) is False


def test_validate_name_with_valid_names():
    # Standard names
    assert validate_name("Player") is True
    assert validate_name("John_Doe") is True
    assert validate_name("Hero-123") is True
    assert validate_name("Test*Name") is True
    assert validate_name("Name[123]") is True
    assert validate_name("~Special~") is True

    # Edge cases
    assert validate_name("a") is True  # Single character
    assert validate_name("a" * 28) is True  # Max length


def test_validate_name_with_invalid_names():
    # Empty name
    assert validate_name("") is False

    # Too long (> 28 characters)
    assert validate_name("a" * 29) is False

    # Invalid characters
    assert validate_name("Name@Email") is False
    assert validate_name("Name!") is False
    assert validate_name("Name#123") is False
    assert validate_name("Name Space") is False  # Space not allowed
    assert validate_name("Name.Dot") is False
    assert validate_name("Name,Comma") is False


def test_validate_name_with_special_allowed_characters():
    # Test each special allowed character
    assert validate_name("Name_underscore") is True
    assert validate_name("Name-dash") is True
    assert validate_name("Name*star") is True
    assert validate_name("Name[bracket]") is True
    assert validate_name("Name~tilde") is True


def test_validate_sex_with_valid_values():
    assert validate_sex(0) is True  # Male
    assert validate_sex(1) is True  # Female


def test_validate_sex_with_invalid_values():
    assert validate_sex(2) is False
    assert validate_sex(-1) is False
    assert validate_sex(100) is False
    assert validate_sex("0") is False  # String, not int
    assert validate_sex(None) is False
    assert validate_sex(0.5) is False


def test_validate_at_least_one_arg_with_one_non_none():
    assert validate_at_least_one_arg("value") is True
    assert validate_at_least_one_arg(0) is True
    assert validate_at_least_one_arg(False) is True  # False is not None
    assert validate_at_least_one_arg("") is True  # Empty string is not None


def test_validate_at_least_one_arg_with_multiple_args():
    assert validate_at_least_one_arg(None, "value", None) is True
    assert validate_at_least_one_arg(None, None, 123) is True
    assert validate_at_least_one_arg("first", None, None) is True


def test_validate_at_least_one_arg_with_all_none():
    assert validate_at_least_one_arg(None) is False
    assert validate_at_least_one_arg(None, None, None) is False


def test_validate_at_least_one_arg_with_no_args():
    assert validate_at_least_one_arg() is False


def test_validate_at_least_one_arg_with_mixed_types():
    assert validate_at_least_one_arg(None, [], None) is True  # Empty list is not None
    assert validate_at_least_one_arg(None, {}, None) is True  # Empty dict is not None
    assert validate_at_least_one_arg(None, 0, None) is True  # Zero is not None
