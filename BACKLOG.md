# Development Backlog for mb-app

This backlog follows Claude Code best practices for task planning and project improvement.

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

## 7. Fix Character Generation Directory Creation
**Priority: High**
**Goal: Ensure profiles directory exists before generating characters**

### Tasks:
- [ ] Add directory creation logic in `service.py`:
  - [ ] Check if profiles directory exists before generating
  - [ ] Create directory structure if missing
  - [ ] Handle both standard and WSE2 paths
- [ ] Update `generate_n_random_characters()`:
  - [ ] Add try/except for directory creation
  - [ ] Provide informative error messages
- [ ] Add tests for directory creation:
  - [ ] Test generation with missing directory
  - [ ] Test permission errors
  - [ ] Test cross-platform paths
- [ ] Consider adding `--init` command to set up game directories

### Acceptance Criteria:
- Character generation works even if profiles directory doesn't exist
- Proper error messages for permission issues
- Works for both standard and WSE2 installations
- No silent failures

## 8. List Characters Feature
**Priority: Medium**
**Goal: Add ability to list all characters in the main profiles file**

### Tasks:
- [ ] Add `--list` flag to argparser:
  - [ ] Show character names from profiles.dat
  - [ ] Optional verbose mode to show more details
- [ ] Implement character listing in `service.py`:
  - [ ] `list_characters()` - Extract and display all character names
  - [ ] Support both standard and WSE2 profiles
  - [ ] Show character count
- [ ] Add parsing logic in `helpers.py`:
  - [ ] Extract character names from binary data
  - [ ] Handle different character data formats
  - [ ] Parse character metadata if needed
- [ ] Add tests for listing functionality:
  - [ ] Test with various character counts
  - [ ] Test with corrupted files
  - [ ] Test empty profiles
- [ ] Consider JSON/CSV export options for the list

### Acceptance Criteria:
- Can list all character names from profiles.dat
- Clear output format
- Handles edge cases gracefully
- Option for detailed output
- Well-tested functionality

## Notes for Claude Code

When implementing these changes:
1. Always run tests after changes
2. Update CLAUDE.md with new commands
3. Maintain backward compatibility
4. Document breaking changes
5. Create atomic commits for each task