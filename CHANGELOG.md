# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [0.3.0] - 2025-06-08


### Added

### Changed

### Fixed

## [0.2.0] - 2025-06-08


### Added

### Changed

### Fixed

## [0.1.2] - 2025-05-30


### Added

### Changed

### Fixed

## [0.1.1] - 2025-05-30


### Added

### Changed

### Fixed

## [0.1.0] - 2025-05-30


### Added
- Centralized version management in `appearance/__version__.py`
- Character deletion feature (planned) - see BACKLOG.md

### Changed
- Version is now sourced from a single location for consistency

## [0.0.7] - 2025-05-30

### Added
- Comprehensive pytest-based test suite with 99.52% coverage
- Modern Python tooling configuration (ruff, mypy, black)
- Development dependencies in requirements-dev.txt
- BACKLOG.md for tracking future development tasks

### Changed
- Replaced all print statements with proper logging
- Added --quiet flag to suppress output except errors
- Improved error handling and logging throughout

## [0.0.6] - 2025-05-29

### Added
- WSE2 (Mount & Blade II: Bannerlord) support via --wse2 flag
- CLAUDE.md with development guidelines and conventions
- Cross-platform profiles directory detection

### Changed
- Service functions now accept wse2 parameter
- Dynamic profile path resolution based on game version

## [0.0.5] - 2022-08-20

### Added
- List backups feature with -s/--show flag
- Display backup file contents

### Changed
- Improved backup listing functionality

## [0.0.4] - 2022-07-27

### Fixed
- Resources folder path resolution
- Package distribution includes necessary resource files

## [0.0.3] - 2022-07-27

### Added
- PyPI package setup
- Proper package structure with setup.py
- Console entry point as `mb-app`

## [0.0.2] - 2022-07-26

### Added
- Character generation feature (-g/--generate N)
- Random character creation with customizable attributes
- Resource templates for character generation

## [0.0.1] - 2022-07-26

### Added
- Initial release
- Backup functionality (-b/--backup)
- Restore functionality (-r/--restore)
- Cross-platform support (Windows, Linux, macOS)
- Automatic Mount & Blade directory detection
- Binary file manipulation for character appearance

[Unreleased]: https://github.com/doppelmarker/mb_appearance/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/doppelmarker/mb_appearance/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/doppelmarker/mb_appearance/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/doppelmarker/mb_appearance/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/doppelmarker/mb_appearance/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.7...v0.1.0
[0.0.7]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/doppelmarker/mb_appearance/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/doppelmarker/mb_appearance/releases/tag/v0.0.1