# Development Backlog for mb-app

This backlog follows Claude Code best practices for task planning and project improvement.

## 1. Unit Testing Suite
**Priority: High**
**Goal: Achieve >80% test coverage for critical binary manipulation logic**

### Tasks:
- [ ] Set up pytest framework and test structure
- [ ] Write tests for `helpers.py`:
  - [ ] `read_header()` with valid/invalid files
  - [ ] `read_profiles()` with various profile counts
  - [ ] `write_profiles()` data integrity
  - [ ] `character_extractor()` edge cases
  - [ ] `data_sticker()` boundary conditions
- [ ] Write tests for `service.py`:
  - [ ] `backup()` functionality
  - [ ] `restore()` with valid/invalid backups
  - [ ] `create_random()` character generation
  - [ ] `list_backups()` output
- [ ] Write tests for `validators.py`:
  - [ ] Path validation logic
  - [ ] Cross-platform path detection
- [ ] Add integration tests for full workflows
- [ ] Configure coverage reporting

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

## 3. GitHub Workflow Setup
**Priority: Medium**
**Goal: Automate testing, linting, and deployment**

### Tasks:
- [ ] Create `.github/workflows/` directory
- [ ] Add `test.yml` workflow:
  - [ ] Run on push/PR
  - [ ] Test matrix (Python 3.8-3.12)
  - [ ] OS matrix (ubuntu, windows, macos)
  - [ ] Coverage reporting to PR
- [ ] Add `lint.yml` workflow:
  - [ ] Run ruff/black/isort
  - [ ] Type checking with mypy
  - [ ] Security checks with bandit
- [ ] Add `release.yml` workflow:
  - [ ] Trigger on version tags
  - [ ] Build wheel and sdist
  - [ ] Upload to PyPI
  - [ ] Create GitHub release
- [ ] Add status badges to README

### Acceptance Criteria:
- All workflows passing
- Automated PyPI deployment working
- PR checks enforced
- Version bumping automated

## 4. Pre-commit Hooks
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
   - Pre-commit hooks
   - GitHub workflows
   - CI/CD pipeline

## Success Metrics

- [x] Zero print statements in codebase (✅ Completed)
- [ ] >80% test coverage
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