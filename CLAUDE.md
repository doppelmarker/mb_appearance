# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `mb-app`, a Python CLI utility for manipulating Mount & Blade character appearance files. The tool can backup, restore, and generate random characters by directly manipulating the game's binary `profiles.dat` file.

## Development Commands

**IMPORTANT: Always activate the virtual environment before running commands**
- **Activate venv**: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
- **Install for development**: `pip install -e .`
- **Run tests**: `python -m pytest tests/ -v`
- **Run the CLI**: `python -m appearance` or `mb-app` (after install)
- **Package for PyPI**: `python setup.py sdist bdist_wheel`

## Architecture

The application follows a clear separation of concerns:

- **Entry point**: `appearance/__main__.py` and `appearance/app.py:main()`
- **CLI parsing**: `argparser.py` handles all command-line arguments
- **Core logic**: `service.py` contains backup/restore/generation functions
- **Binary manipulation**: `helpers.py` handles low-level file I/O and byte operations
- **File paths**: `consts.py` manages cross-platform game directory detection and binary offsets

## Key Technical Details

- **Cross-platform support**: Automatically detects Mount & Blade directory on Windows, Linux, and macOS
- **Binary file format**: Manipulates specific byte offsets for character properties (name, sex, skin, appearance)
- **Resource files**: Uses bundled template files (`header.dat`, `common_char.dat`) for character generation
- **Backup system**: Stores backups in `resources/backups/` with `.dat` extension

## File Structure

- Core application logic in `appearance/` package
- Binary templates and backups in `resources/`
- Console entry point configured in `setup.py` as `mb-app`

## Testing Guidelines

**IMPORTANT: Testing Philosophy and Preferences**

- **Use pytest-style tests exclusively**: Write tests as simple functions with assertions, not as unittest classes
- **NO MOCKS**: Avoid using mocks (`unittest.mock`, `pytest-mock`, etc.). Instead:
  - Design the system to be modular with clear interfaces
  - Use dependency injection to allow easy substitution of components
  - Create simple stub implementations for testing
  - Make each module easily replaceable to enhance testability
- **NO MONKEYPATCH**: Avoid using pytest's `monkeypatch` fixture. Instead:
  - Use dependency injection to pass in test-specific values
  - Design functions to accept parameters for external dependencies
  - Create test fixtures that set up the environment naturally
- **Test-Driven Development (TDD)**: Write tests first, then implementation
- **Integration over isolation**: Prefer testing real behavior over mocked interactions
- **Stubs over mocks**: When isolation is needed, create minimal stub implementations

### Example of preferred testing style:

```python
# GOOD: pytest-style with stub and dependency injection
def test_backup_creates_file(tmp_path):
    stub_profiles_path = tmp_path / "profiles.dat"
    stub_profiles_path.write_bytes(b"test data")
    
    backup_path = tmp_path / "backup.dat"
    backup(str(backup_path), profiles_path=stub_profiles_path)
    
    assert backup_path.exists()
    assert backup_path.read_bytes() == b"test data"

# GOOD: Using test parameters instead of monkeypatch
def test_argparser_with_list_option():
    # Instead of monkeypatch.setattr(sys, "argv", ["mb-app", "-l"])
    parser = ArgParser()
    args = parser.parser.parse_args(["-l"])
    assert args.list is True

# BAD: unittest-style with mocks
class TestBackup(unittest.TestCase):
    @mock.patch('appearance.service.read_profiles')
    def test_backup(self, mock_read):
        mock_read.return_value = b"test"
        # ... etc

# BAD: Using monkeypatch
def test_something(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mb-app", "-l"])
    # ... etc
```

### Architectural considerations for testability:

1. Use dependency injection for file paths and external dependencies
2. Create interfaces/protocols for components that need substitution
3. Keep functions pure where possible
4. Separate I/O operations from business logic

## Version Management

### Bumping Version
Use the `bump_version.py` script to update version:

```bash
# Patch version (bug fixes): 0.0.7 → 0.0.8
python bump_version.py patch

# Minor version (new features): 0.0.7 → 0.1.0
python bump_version.py minor

# Major version (breaking changes): 0.0.7 → 1.0.0
python bump_version.py major

# Skip git operations (for testing)
python bump_version.py patch --no-git

# Skip CHANGELOG update
python bump_version.py patch --no-changelog

# Skip README usage update
python bump_version.py patch --no-readme
```

The script will:
1. Update `appearance/__version__.py`
2. Update `README.md` usage section with latest `mb-app -h` output
3. Update `CHANGELOG.md` with new version section
4. Create git commit and tag
5. Provide next steps for release

### Version Guidelines
- **Patch**: Bug fixes, documentation updates, minor improvements
- **Minor**: New features, non-breaking enhancements
- **Major**: Breaking changes, major refactoring
- Stay in 0.x.x until API is stable

## Binary File Format Details

**CRITICAL: Understanding Mount & Blade profiles.dat Structure**

Through extensive debugging and testing, we've reverse-engineered the binary structure of Mount & Blade character files:

### File Structure Overview
```
profiles.dat:
├── Header (12 bytes)
│   ├── Offset 0-3: Unknown/magic bytes
│   ├── Offset 4-7: Character count (little-endian)
│   └── Offset 8-11: Character count duplicate (little-endian)
└── Character Data (89+ bytes per character)
```

### Character Data Structure (per character)
**IMPORTANT**: Each character is exactly 89 bytes minimum (`MIN_BYTES_AMOUNT_FOR_CHAR`)

```
Character Block (89 bytes):
├── Offset 0: Name length (1 byte)
├── Offset 1-3: Padding (3 bytes, usually 0x00)
├── Offset 4: First character of name
├── Offset 5: SEX byte (0=Male, 1=Female) - OVERLAPS WITH NAME!
├── Offset 6+: Rest of name data
├── Offset 9-12: Banner data (4 bytes, 0xFFFFFFFF = Current Nation)
├── Offset 13: HAIRSTYLE byte (0+ = hair type/style options)
├── Offset 14: SKIN byte (0=White, 16=Light, 32=Tan, 48=Dark, 64=Black)
├── Offset 16-17: AGE + HAIR COLOR (bit-packed, see below)
├── Offset 21-31: Appearance bytes (11 bytes of random character features)
└── Padding to 89 bytes minimum
```

### Bit-Packed Age and Hair Color Format
**CRITICAL**: Age and Hair Color share bytes 16-17 using bit-packing:

```
Byte 16 (shared):
├── Bits 0-5: Hair Color (6 bits, 0-63 full range)
└── Bits 6-7: Age low 2 bits

Byte 17:
├── Bits 0-3: Age high 4 bits (Age uses 6 bits total)
└── Bits 4-7: Unused/reserved

Age formula: age = ((byte_16 & 0xC0) >> 6) + ((byte_17 & 0x0F) << 2)
Hair Color formula: hair_color = byte_16 & 0x3F
```

### Critical Constants (from consts.py)
```python
CHAR_OFFSETS = {
    "NAME_LENGTH": 0,         # Offset to name length byte
    "NAME": 4,                # Offset to name start
    "SEX": 5,                 # Offset to sex byte (overlaps with name!)
    "BANNER": 9,              # Offset to banner (4 bytes)
    "HAIRSTYLE": 13,          # Offset to hair style (1 byte)
    "SKIN": 14,               # Offset to skin byte
    "AGE_HAIR_COLOR": 16,     # Offset to bit-packed age/hair color (2 bytes)
    "APPEARANCE": 21,         # Offset to appearance bytes (11 bytes)
}
```

### Known Issues & Solutions

#### Bug #9: Sample Reuse Corruption (FIXED)
**Problem**: Original code reused the same `sample` template for all characters:
```python
# BROKEN CODE:
for char_idx in range(n):
    sample = sample[0:sex_offset] + get_random_sex() + sample[sex_offset + 1:]
    # This modifies the template for subsequent characters!
```

**Solution**: Create fresh copy for each character:
```python
# FIXED CODE:
for char_idx in range(n):
    char_data = sample[:]  # Fresh copy!
    char_data = char_data[0:sex_offset] + get_random_sex() + char_data[sex_offset + 1:]
```

### Resource Files
- **`resources/header.dat`**: 12-byte header template
- **`resources/common_char.dat`**: Contains 12-byte header + 89-byte character template
- **Character template starts at offset 12** in `common_char.dat`

### Testing with Binary Data
**IMPORTANT**: When creating test data, always use real character generation instead of hardcoded binary data. The character structure is complex with overlapping fields, making manual binary construction error-prone.

```python
# GOOD: Use real generation
generate_n_random_characters(3, profiles_file_path=test_file, ...)
characters = list_characters(profiles_file_path=test_file)

# BAD: Manual binary construction
char_data = b"\x04\x00\x00\x00Test\x00..."  # Fragile and error-prone
```

### Valid Values
- **Sex**: 0 (Male) or 1 (Female)
- **Skin**: 0 (White), 16 (Light), 32 (Tan), 48 (Dark), 64 (Black)
- **Hair Style**: 0+ (various hair styles, 0 typically = bald/minimal)
- **Hair Color**: 0-3 (bit-packed in byte 16, bits 4-5)
- **Age**: 0-63 typical range (10-bit value split across bytes 16-17)
- **Banner**: 0xFFFFFFFF = Current Nation, other values = specific banners
- **Any other values indicate data corruption**

### Reverse Engineering Notes
The actual Mount & Blade binary format was reverse-engineered through:
1. Analysis of the `resources/mb_characters_bytes.png` diagram
2. Binary comparison of game-generated files with different character settings
3. Bit-level analysis revealing the packed Age/Hair Color format in bytes 16-17

Key discoveries:
- Age and Hair Color share byte 16 through bit-packing
- Character offsets 13 (hair style) and 16-17 (age/hair color) were previously unknown
- The format uses efficient bit-packing to store multiple values in shared bytes

## Commit Guidelines

When Claude generates commits, use the following format:
- Prefix with `[Claude]` to indicate AI-generated commits
- Follow conventional commit patterns: `[feat]`, `[fix]`, `[docs]`, `[refactor]`, `[test]`, `[chore]`
- Example: `[Claude][feat] Add new character generation feature`
- Example: `[Claude][fix] Fix cross-platform directory detection`