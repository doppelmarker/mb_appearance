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
- **Test-Driven Development (TDD)**: Write tests first, then implementation
- **Integration over isolation**: Prefer testing real behavior over mocked interactions
- **Stubs over mocks**: When isolation is needed, create minimal stub implementations

### Example of preferred testing style:

```python
# GOOD: pytest-style with stub
def test_backup_creates_file(tmp_path):
    stub_profiles_path = tmp_path / "profiles.dat"
    stub_profiles_path.write_bytes(b"test data")
    
    backup_path = tmp_path / "backup.dat"
    backup(str(backup_path), profiles_path=stub_profiles_path)
    
    assert backup_path.exists()
    assert backup_path.read_bytes() == b"test data"

# BAD: unittest-style with mocks
class TestBackup(unittest.TestCase):
    @mock.patch('appearance.service.read_profiles')
    def test_backup(self, mock_read):
        mock_read.return_value = b"test"
        # ... etc
```

### Architectural considerations for testability:

1. Use dependency injection for file paths and external dependencies
2. Create interfaces/protocols for components that need substitution
3. Keep functions pure where possible
4. Separate I/O operations from business logic

## Commit Guidelines

When Claude generates commits, use the following format:
- Prefix with `[Claude]` to indicate AI-generated commits
- Follow conventional commit patterns: `[feat]`, `[fix]`, `[docs]`, `[refactor]`, `[test]`, `[chore]`
- Example: `[Claude][feat] Add new character generation feature`
- Example: `[Claude][fix] Fix cross-platform directory detection`