# Development Backlog for mb-app

This backlog follows Claude Code best practices for task planning and project improvement.

## 1. Unit Testing Suite
**Priority: High**
**Goal: Achieve >80% test coverage for critical binary manipulation logic**

### Tasks:
- [x] Set up pytest framework and test structure
- [x] Write tests for `helpers.py`:
  - [x] `read_profiles()` and `write_profiles()` with valid/invalid files
  - [x] `int_to_hex_bytes()` with various values
  - [x] `get_name_length()` with different terminators
  - [x] `get_header_with_chars_amount()` header updates
  - [x] Random generation functions (byte, sex, skin)
- [x] Write tests for `service.py`:
  - [x] `backup()` functionality
  - [x] `restore_from_backup()` with valid/invalid backups
  - [x] `generate_n_random_characters()` character generation
  - [x] `show_backuped_characters()` output
- [x] Write tests for `validators.py`:
  - [x] Path validation logic
  - [x] All validation functions tested
- [x] Configure coverage reporting

### Acceptance Criteria:
- Test coverage >80% for core modules
- All edge cases covered
- Tests pass on Windows/Linux/macOS
- CI/CD integration ready

## 2. Project Structure Improvements
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

## 5. Character Deletion Feature
**Priority: Medium**
**Goal: Add ability to delete characters from profiles.dat**

### Tasks:
- [ ] Add `--delete` flag to argparser:
  - [ ] Support no arguments (delete all characters)
  - [ ] Support character name arguments (delete specific characters)
  - [ ] Add confirmation prompt for safety
- [ ] Implement deletion logic in `service.py`:
  - [ ] `delete_all_characters()` - Remove all characters from profiles
  - [ ] `delete_characters_by_name(names)` - Remove specific characters
  - [ ] Preserve file structure integrity after deletion
- [ ] Add helper functions in `helpers.py`:
  - [ ] Parse character blocks from profiles
  - [ ] Rebuild profiles after deletion
  - [ ] Update header with new character count
- [ ] Add comprehensive tests:
  - [ ] Test delete all functionality
  - [ ] Test selective deletion by name
  - [ ] Test edge cases (non-existent names, empty file)
- [ ] Update documentation:
  - [ ] Add usage examples to README
  - [ ] Document safety considerations

### Acceptance Criteria:
- Characters can be deleted safely
- File integrity maintained after deletion
- Confirmation required for destructive operations
- Comprehensive error handling
- Feature well-documented

## 6. Pre-commit Hooks
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

## Execution Order

1. **Phase 1 - Quality** (Week 1)
   - Basic test structure setup
   - Complete unit tests

2. **Phase 2 - Structure** (Week 2)
   - Project structure improvements
   - Package modernization

3. **Phase 3 - Automation** (Week 3)
   - Add Makefile
   - Pre-commit hooks
   - GitHub workflows
   - CI/CD pipeline

## Success Metrics

- [x] Zero print statements in codebase (✅ Completed)
- [x] >80% test coverage (✅ Achieved 99.52% coverage)
- [ ] All CI checks passing
- [ ] Automated release process
- [ ] Clean pip install from PyPI
- [ ] Contributing guide complete

## Notes for Claude Code

When implementing these changes:
1. Always run tests after changes
2. Update CLAUDE.md with new commands
3. Maintain backward compatibility
4. Document breaking changes
5. Create atomic commits for each task