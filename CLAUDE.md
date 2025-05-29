# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `mb-app`, a Python CLI utility for manipulating Mount & Blade character appearance files. The tool can backup, restore, and generate random characters by directly manipulating the game's binary `profiles.dat` file.

## Development Commands

- **Install for development**: `pip install -e .`
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

## Commit Guidelines

When Claude generates commits, use the following format:
- Prefix with `[Claude]` to indicate AI-generated commits
- Follow conventional commit patterns: `[feat]`, `[fix]`, `[docs]`, `[refactor]`, `[test]`, `[chore]`
- Example: `[Claude][feat] Add new character generation feature`
- Example: `[Claude][fix] Fix cross-platform directory detection`