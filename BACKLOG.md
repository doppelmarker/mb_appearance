# Development Backlog for mb-app

This backlog follows Claude Code best practices for task planning and project improvement.

**IMPORTANT**: This project serves as the foundation for the warband-face-editor (https://github.com/doppelmarker/warband-face-editor), a web-based 3D character face customization tool. Features are prioritized based on their importance for enabling web-based face editing functionality.

## 🎉 MAJOR MILESTONE ACHIEVED - December 2024
**Face Code Support Implementation Complete!**

We have successfully implemented full Mount & Blade Warband face code support with:
- ✅ Complete 43-morph face code parsing (exactly matching game format)
- ✅ Perfect round-trip encoding/decoding (verified with game examples)  
- ✅ All appearance parameters (hair, beard, age, skin, hair_color)
- ✅ Comprehensive test suite (7 tests, all passing)
- ✅ Ready for web editor integration

**This unlocks the path to the web-based 3D face editor!** The next critical step is creating a FastAPI wrapper to expose these functions as REST endpoints.

## ✅ COMPLETED: Face Code Support
**Priority: CRITICAL - COMPLETED December 2024**
**Goal: Enable parsing and generation of Mount & Blade Warband's 64-character hexadecimal face codes**

### Background:
Mount & Blade Warband uses 64-character face codes (e.g., "0x000000018000004136db79b6db6db6fb...") that encode:
- 43 morph targets (3 bits each, last one 1 bit) for detailed face shape
- Hair index (6 bits)
- Beard index (6 bits) 
- Age (6 bits)
- Skin tone (6 bits)
- Hair color (6 bits)
- Additional appearance parameters

### ✅ Completed Tasks:
- [x] **Face code parsing module** (`parse_face_code_components()`):
  - [x] Parse 64-char hex string to structured data using correct 4-block layout
  - [x] Extract all 43 morph values (morph_keys 0-42)
  - [x] Extract hair, beard, age, skin, hair_color parameters
  - [x] Validate face code format with comprehensive error handling
- [x] **Face code generation** (`generate_face_code()`):
  - [x] Convert structured data to hex code with proper bit packing
  - [x] Handle 4-block structure (64 bits each)
  - [x] Generate valid 64-char codes matching game format
- [x] **Character data integration** (`apply_face_code()`):
  - [x] Map face codes to binary character bytes at correct offsets
  - [x] Support bit-packed age/hair_color in bytes 16-17
  - [x] Write appearance data to profiles.dat format
- [x] **Comprehensive test suite**:
  - [x] Test known face codes from internal_format.txt documentation
  - [x] Perfect round-trip conversion tests (encode → decode → encode)
  - [x] Edge case validation (invalid inputs, missing components)
  - [x] Value clamping tests (bit range enforcement)
  - [x] Documentation example verification (age=6 correctly extracted)

### ✅ Technical Achievements:
- **Accurate bit-packing**: Implements correct 4-block structure from Mount & Blade documentation
- **Perfect compatibility**: Face codes match game's Ctrl+E export format exactly  
- **Robust validation**: Handles both 0x-prefixed and plain hex formats
- **Complete API**: Both parsing and generation with full component access
- **Production ready**: 7 comprehensive tests, all passing

### ✅ Integration Points:
- Face codes displayed in character listings with `--show-face-codes` flag
- Components accessible programmatically for web editor integration
- Ready for FastAPI wrapper to expose as REST endpoints

## NEXT: FastAPI Web Service Wrapper
**Priority: CRITICAL - IMMEDIATE NEXT STEP**
**Goal: Create minimal web API to expose face code functionality for the warband-face-editor**

### Tasks:
- [ ] **Create `web_api.py` with FastAPI**:
  - [ ] POST `/api/profiles/upload` - Upload profiles.dat, return character list with face codes
  - [ ] GET `/api/face-code/{face_code}/decode` - Decode face code to components
  - [ ] POST `/api/face-code/encode` - Encode components to face code
  - [ ] PUT `/api/characters/{session_id}/{index}/face` - Update character face code
  - [ ] GET `/api/profiles/{session_id}/download` - Download modified profiles.dat
- [ ] **Session management**:
  - [ ] In-memory session storage for uploaded files
  - [ ] Session-based character modifications
  - [ ] Auto-cleanup of old sessions
- [ ] **CORS configuration**:
  - [ ] Enable CORS for browser access
  - [ ] Configure for development and production
- [ ] **Error handling**:
  - [ ] Proper HTTP status codes
  - [ ] Validation error messages
  - [ ] Face code format validation
- [ ] **Docker deployment**:
  - [ ] Create Dockerfile for web service
  - [ ] docker-compose.yml for easy startup
  - [ ] Environment configuration

### Acceptance Criteria:
- Web API exposes all face code functionality
- Browser can upload/download profiles.dat files
- Face codes can be decoded/encoded via REST
- Characters can be modified through API
- Ready for Three.js frontend integration

## THEN: Library API Exposure  
**Priority: HIGH**
**Goal: Make mb-app usable as a Python library (longer-term refactoring)**

### Tasks:
- [ ] Create public API module (`appearance.api`):
  - [ ] Character class with properties
  - [ ] ProfilesManager for file operations
  - [ ] FaceCodeParser for face code handling
  - [ ] Clean separation from CLI code
- [ ] Add programmatic interfaces:
  - [ ] `load_profiles()` - Load profiles data
  - [ ] `get_character()` - Get single character
  - [ ] `update_character()` - Modify character
  - [ ] Face code functions already implemented ✅
- [ ] Add async support for web integration:
  - [ ] Async file operations
  - [ ] Thread-safe character access
  - [ ] Concurrent operation support
- [ ] Create API documentation:
  - [ ] Sphinx docs setup
  - [ ] API reference
  - [ ] Usage examples
  - [ ] Web integration guide

### Acceptance Criteria:
- Can import and use mb-app in Python code
- Clean API without CLI dependencies
- Thread-safe for web usage
- Comprehensive API documentation

## 7. Import/Export Feature (UPDATED)
**Priority: CRITICAL**
**Goal: Enable character data exchange with web-based face editor**

### Updated Tasks:
- [ ] Add JSON export with face codes:
  - [ ] Include 64-char face code in export
  - [ ] Structure suitable for web API
  - [ ] Support single and bulk export
  - [ ] Include all morph/appearance data
- [ ] Add JSON import with validation:
  - [ ] Import from web editor format
  - [ ] Validate face codes
  - [ ] Handle partial data updates
  - [ ] Preserve non-appearance data
- [ ] Add REST API format support:
  - [ ] Export format matching web API needs
  - [ ] Structured morph target data
  - [ ] Include metadata (version, timestamp)
- [ ] Original tasks remain...

## 1. Project Structure Improvements
**Priority: Medium**
**Goal: Align with Python packaging best practices**

### Tasks:
- [ ] Move backup storage outside of package:
  - [ ] Change default to `~/.mb_app/backups/`
  - [ ] Add migration script for existing backups
  - [ ] Update `consts.py` with new paths
- [ ] Fix `MANIFEST.in`:
  - [ ] Include only necessary resource files
  - [ ] Exclude development files
  - [ ] Add proper wildcards
- [ ] Modernize `setup.py`:
  - [ ] Convert to `pyproject.toml` (PEP 517/518)
  - [ ] Use `setuptools_scm` for versioning
  - [ ] Add proper classifiers
  - [ ] Define extras_require for dev dependencies
- [ ] Add `__version__` to package
- [ ] Create proper package metadata

### Acceptance Criteria:
- Backups stored in user directory, not package
- Clean pip installation works
- Version management automated
- Package metadata complete

## 3. Add Makefile
**Priority: Medium**
**Goal: Standardize development commands and simplify workflow**

### Tasks:
- [ ] Create `Makefile` with common commands:
  - [ ] `make install` - Install package in development mode
  - [ ] `make test` - Run test suite
  - [ ] `make coverage` - Run tests with coverage report
  - [ ] `make lint` - Run linting tools (ruff, black, isort)
  - [ ] `make format` - Auto-format code
  - [ ] `make typecheck` - Run mypy type checking
  - [ ] `make build` - Build distribution packages
  - [ ] `make clean` - Clean build artifacts
  - [ ] `make release` - Tag and prepare release
- [ ] Add help target with command descriptions
- [ ] Document Makefile usage in README

### Acceptance Criteria:
- All common dev tasks have make commands
- Works cross-platform (with make installed)
- Self-documenting with `make help`
- GitHub workflows use Makefile commands

## 4. GitHub Workflow Setup
**Priority: Medium**
**Goal: Automate testing, linting, and deployment**

### Tasks:
- [ ] Create `.github/workflows/` directory
- [ ] Add `test.yml` workflow:
  - [ ] Run on push/PR
  - [ ] Test matrix (Python 3.8-3.12)
  - [ ] OS matrix (ubuntu, windows, macos)
  - [ ] Coverage reporting to PR
  - [ ] Use Makefile commands (e.g., `make test`)
- [ ] Add `lint.yml` workflow:
  - [ ] Run ruff/black/isort via `make lint`
  - [ ] Type checking with mypy via `make typecheck`
  - [ ] Security checks with bandit
- [ ] Add `release.yml` workflow:
  - [ ] Trigger on version tags
  - [ ] Build wheel and sdist via `make build`
  - [ ] Upload to PyPI
  - [ ] Create GitHub release
- [ ] Add status badges to README

### Acceptance Criteria:
- All workflows passing
- Automated PyPI deployment working
- PR checks enforced
- Version bumping automated
- Workflows use Makefile commands for consistency

## 5. Character Editing Feature
**Priority: High**
**Goal: Add ability to modify existing characters without deleting/recreating**

### Tasks:
- [ ] Add `--edit` flag to argparser:
  - [ ] Support character index or name as identifier
  - [ ] Add sub-options for each editable attribute
  - [ ] Allow multiple edits in one command
- [ ] Implement editing logic in `service.py`:
  - [ ] `edit_character()` - Main editing function
  - [ ] Support name changes
  - [ ] Support sex changes
  - [ ] Support skin color changes
  - [ ] Support age modifications
  - [ ] Support hair style/color changes
  - [ ] Support appearance bytes editing
- [ ] Add validation for edit operations:
  - [ ] Ensure valid attribute values
  - [ ] Prevent duplicate names
  - [ ] Validate character exists
- [ ] Add comprehensive tests:
  - [ ] Test each attribute modification
  - [ ] Test multiple edits at once
  - [ ] Test edge cases
- [ ] Update documentation with examples

### Acceptance Criteria:
- Can edit any character attribute
- Changes persist correctly in binary file
- Validation prevents invalid values
- Clear error messages for invalid operations
- Well-documented usage examples

## 6. Data Safety Features
**Priority: High**
**Goal: Prevent data loss and add recovery options**

### Tasks:
- [ ] Add automatic backup before destructive operations:
  - [ ] Before delete operations
  - [ ] Before generate operations
  - [ ] Before edit operations
  - [ ] Configurable via --no-auto-backup flag
- [ ] Implement dry-run mode:
  - [ ] Add --dry-run flag to all operations
  - [ ] Show what would happen without making changes
  - [ ] Display affected characters
- [ ] Add data integrity validation:
  - [ ] `--verify` command to check file integrity
  - [ ] Validate header matches character count
  - [ ] Check for corrupted character data
  - [ ] Report issues found
- [ ] Implement undo functionality:
  - [ ] `--undo` command to revert last operation
  - [ ] Store operation history in ~/.mb_app/history/
  - [ ] Limit history to last N operations
- [ ] Add backup rotation:
  - [ ] Keep last N automatic backups
  - [ ] Timestamp-based naming
  - [ ] Cleanup old backups

### Acceptance Criteria:
- Never lose data without user explicitly choosing to
- Can preview any operation before executing
- Can detect and report corruption
- Can undo recent operations
- Automatic backup management

## 7. Import/Export Feature
**Priority: High**
**Goal: Enable character sharing and external tool integration**

### Tasks:
- [ ] Add export functionality:
  - [ ] `--export` flag for single character
  - [ ] `--export-all` flag for all characters
  - [ ] Support JSON format
  - [ ] Support CSV format
  - [ ] Include all character attributes
- [ ] Add import functionality:
  - [ ] `--import` flag to add characters
  - [ ] Support same formats as export
  - [ ] Handle name conflicts
  - [ ] Validate imported data
- [ ] Implement character templates:
  - [ ] Save character as template
  - [ ] Generate from template
  - [ ] Share templates between users
- [ ] Add merge functionality:
  - [ ] Merge characters from another profiles.dat
  - [ ] Handle duplicates intelligently
  - [ ] Preserve character order options

### Acceptance Criteria:
- Can export/import in standard formats
- Data round-trips without loss
- Templates work for appearance presets
- Can merge profiles from multiple sources
- Clear handling of conflicts

## 8. Search and Filter Feature
**Priority: Medium**
**Goal: Help users find specific characters quickly**

### Tasks:
- [ ] Add search functionality to list command:
  - [ ] `--search` flag with pattern support
  - [ ] Support wildcards (*, ?)
  - [ ] Case-insensitive by default
- [ ] Add filter options:
  - [ ] `--filter` flag with attribute=value syntax
  - [ ] Support multiple filters
  - [ ] Filter by sex, skin, age range, etc.
- [ ] Add sort options:
  - [ ] `--sort` flag (name, age, index)
  - [ ] Ascending/descending order
- [ ] Add detailed inspection:
  - [ ] `--inspect` flag for detailed view
  - [ ] Show all attributes in readable format
  - [ ] Show raw bytes optionally
- [ ] Add statistics command:
  - [ ] `--stats` to show character distribution
  - [ ] Count by sex, skin, age ranges
  - [ ] Show name patterns

### Acceptance Criteria:
- Can quickly find characters by name
- Can filter by any attribute
- Can sort list output
- Can inspect character details
- Statistics provide useful insights

## 9. Batch Operations
**Priority: Medium**
**Goal: Efficiently handle multiple character operations**

### Tasks:
- [ ] Enhance delete to support multiple targets:
  - [ ] Accept comma-separated indices
  - [ ] Accept index ranges (1-5)
  - [ ] Mix names and indices
- [ ] Add batch edit functionality:
  - [ ] `--edit-all` with filters
  - [ ] Apply same change to multiple characters
  - [ ] Support conditional edits
- [ ] Add duplicate functionality:
  - [ ] `--duplicate` flag with count
  - [ ] Auto-generate variant names
  - [ ] Optionally vary attributes
- [ ] Add reorder functionality:
  - [ ] `--reorder` with new order
  - [ ] Move characters to specific positions
  - [ ] Sort by attributes
- [ ] Add batch rename:
  - [ ] `--rename-pattern` with templates
  - [ ] Support {index}, {name}, {attribute} placeholders
  - [ ] Preview before applying

### Acceptance Criteria:
- Can operate on multiple characters efficiently
- Batch operations have safety checks
- Clear preview of what will happen
- Undo works for batch operations
- Pattern-based operations are flexible

## 10. Character Generation Improvements
**Priority: Medium**
**Goal: More control over random character creation**

### Tasks:
- [ ] Add constrained generation:
  - [ ] `--sex`, `--skin`, `--age-range` constraints
  - [ ] Apply to all generated characters
  - [ ] Mix constraints with randomization
- [ ] Add name generation options:
  - [ ] `--names-from` file option
  - [ ] `--name-pattern` with templates
  - [ ] Culture-specific name lists
- [ ] Add appearance presets:
  - [ ] `--preset` option (warrior, merchant, noble)
  - [ ] Define presets in config file
  - [ ] Combine presets with randomization
- [ ] Add family generation:
  - [ ] `--family` flag to generate related characters
  - [ ] Similar appearance bytes
  - [ ] Appropriate age distribution
- [ ] Add weighted randomization:
  - [ ] Config file for probability weights
  - [ ] More realistic distributions
  - [ ] User-defined weight profiles

### Acceptance Criteria:
- Can generate characters matching criteria
- Name generation is flexible
- Presets speed up common use cases
- Family generation creates believable groups
- Randomization can be tuned

## 11. Pre-commit Hooks
**Priority: Low**
**Goal: Ensure code quality before commits**

### Tasks:
- [ ] Add `.pre-commit-config.yaml`
- [ ] Configure hooks:
  - [ ] black (code formatting)
  - [ ] ruff (linting)
  - [ ] isort (import sorting)
  - [ ] mypy (type checking)
  - [ ] trailing whitespace
  - [ ] end-of-file fixer
  - [ ] check-added-large-files
- [ ] Add pre-commit to dev dependencies
- [ ] Document setup in CONTRIBUTING.md
- [ ] Add CI check for pre-commit

### Acceptance Criteria:
- Pre-commit runs on all commits
- All hooks passing
- Easy setup for contributors
- CI validates pre-commit compliance

## 12. Interactive Mode
**Priority: Low**
**Goal: Provide user-friendly interface for non-technical users**

### Tasks:
- [ ] Add `--interactive` flag:
  - [ ] Launch menu-driven interface
  - [ ] Use simple prompts library
  - [ ] Support all major operations
- [ ] Implement main menu:
  - [ ] List characters
  - [ ] Generate characters
  - [ ] Edit characters
  - [ ] Delete characters
  - [ ] Backup/Restore
  - [ ] Import/Export
- [ ] Add operation wizards:
  - [ ] Guide through complex operations
  - [ ] Validate input at each step
  - [ ] Show previews before confirming
- [ ] Add help system:
  - [ ] Context-sensitive help
  - [ ] Examples for each operation
  - [ ] Tips and best practices

### Acceptance Criteria:
- Complete operations without memorizing flags
- Clear navigation and prompts
- Validation prevents errors
- Help is always available
- Works on all platforms

## 13. Performance Optimizations
**Priority: High (for web editor)**
**Goal: Handle real-time web operations with minimal latency**

### Tasks:
- [ ] Implement streaming file operations:
  - [ ] Don't load entire file for list/search
  - [ ] Process characters individually
  - [ ] Reduce memory footprint
- [ ] Add indexing for faster operations:
  - [ ] Create index file for quick lookups
  - [ ] Update index on modifications
  - [ ] Rebuild index command
- [ ] Optimize character parsing:
  - [ ] Lazy parsing of attributes
  - [ ] Cache parsed data
  - [ ] Batch read operations
- [ ] Add progress indicators:
  - [ ] Show progress for long operations
  - [ ] ETA for batch operations
  - [ ] Cancelable operations

### Acceptance Criteria:
- Can handle 1000+ characters smoothly
- Memory usage stays reasonable
- Operations show progress
- Performance metrics documented
- No regression in functionality

## Execution Order (Prioritized for warband-face-editor)

### Phase 1 - Critical Web Editor Foundation (Immediate Priority)
1. **Face Code Support** (NEW) - Essential for Warband face editing
2. **Library API Exposure** (NEW) - Enable Python library usage for web service
3. **Import/Export** (#7 UPDATED) - JSON/API format with face codes
4. **Character Editing** (#5) - Core functionality for modifying faces

### Phase 2 - Data Integrity & Performance (Short-term)
1. **Data Safety Features** (#6) - Critical for web editor reliability
2. **Performance Optimizations** (#13) - Important for real-time web response
3. **Search and Filter** (#8) - Character selection for web UI

### Phase 3 - Enhanced Functionality (Medium-term)
1. **Batch Operations** (#9) - Bulk editing from web interface
2. **Character Generation Improvements** (#10) - Test data with face codes
3. **Project Structure Improvements** (#1) - Clean library packaging

### Phase 4 - Development Infrastructure (Lower Priority)
1. **GitHub Workflows** (#4) - Automated testing and releases
2. **Add Makefile** (#3) - Developer convenience
3. **Pre-commit Hooks** (#11) - Code quality
4. **Interactive Mode** (#12) - Less relevant for web-based editor

## Success Metrics

### Already Achieved
- [x] Zero print statements in codebase (✅ Completed)
- [x] >80% test coverage (✅ Achieved 99.52% coverage)
- [x] Character deletion feature (✅ v0.1.0)
- [x] Character listing feature (✅ v0.2.0)
- [x] Fix sample reuse bug (✅ v0.1.2)
- [x] Fix directory creation (✅ v0.1.1)

### Web Editor Foundation Goals
- [x] **Face code parsing/generation (64-char hex)** ✅ COMPLETED
  - [x] Parse 43 morph values + appearance parameters
  - [x] Generate valid face codes from components  
  - [x] Perfect round-trip encoding/decoding
  - [x] Match game's Ctrl+E format exactly
- [ ] FastAPI web service wrapper (NEXT)
- [ ] Python library API for web integration  
- [ ] JSON export with face codes and morph data
- [ ] Thread-safe character operations
- [ ] REST API-compatible data formats

### Core Feature Goals
- [ ] Character editing without delete/recreate
- [ ] Auto-backup before destructive operations
- [ ] JSON export/import functionality
- [ ] Character search and filtering
- [ ] Batch operations support

### Infrastructure Goals
- [ ] All CI checks passing
- [ ] Automated release process
- [ ] Clean pip install from PyPI
- [ ] Contributing guide complete
- [ ] Makefile for common tasks

### User Experience Goals
- [ ] Dry-run mode for all operations
- [ ] Undo functionality
- [ ] Interactive mode for beginners
- [ ] Comprehensive --help documentation
- [ ] Example usage in README

## Notes for Claude Code

When implementing these changes:
1. Always run tests after changes
2. Update CLAUDE.md with new commands
3. Maintain backward compatibility
4. Document breaking changes
5. Create atomic commits for each task
6. **Consider web editor integration** - Features should be designed with Python library usage in mind
7. **Prioritize face code support** - This is critical for the warband-face-editor project
8. **Design for async/thread-safety** - Web services need concurrent access