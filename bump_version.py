#!/usr/bin/env python3
"""Version bump utility for mb-app."""
import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_current_version():
    """Read current version from __version__.py."""
    version_file = Path("appearance/__version__.py")
    content = version_file.read_text()
    match = re.search(r'__version__ = "(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("Could not find version in __version__.py")
    return match.group(1)


def bump_version(current_version, bump_type):
    """Calculate new version based on bump type."""
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_file(new_version):
    """Update __version__.py with new version."""
    version_file = Path("appearance/__version__.py")
    content = f'"""Version information for mb-app."""\n__version__ = "{new_version}"'
    version_file.write_text(content)


def update_readme_usage():
    """Update README.md with latest help output from mb-app."""
    readme_file = Path("README.md")
    
    # Get the current help output
    try:
        result = subprocess.run(
            [sys.executable, "-m", "appearance", "-h"],
            capture_output=True,
            text=True,
            check=True
        )
        help_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not get help output: {e}")
        return False
    
    # Read current README
    content = readme_file.read_text()
    
    # Find the usage section and replace it
    # Match from "usage: mb-app" to the line before "## Examples" or similar
    pattern = r"(## Usage\n\n)(    usage: mb-app.*?)(\n\n## )"
    
    # Format the help output with proper indentation
    indented_help = "\n".join("    " + line if line else "" for line in help_output.strip().split("\n"))
    
    # Replace the usage section
    new_content = re.sub(
        pattern,
        rf"\1{indented_help}\3",
        content,
        flags=re.DOTALL
    )
    
    if new_content != content:
        readme_file.write_text(new_content)
        return True
    return False


def update_changelog(old_version, new_version, bump_type):
    """Update CHANGELOG.md with new version section."""
    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create new version section
    new_section = f"""## [Unreleased]

### Added

### Changed

### Fixed

## [{new_version}] - {today}
"""
    
    # Replace the current [Unreleased] section
    pattern = r"## \[Unreleased\]"
    content = re.sub(pattern, new_section, content, count=1)
    
    # Update comparison links at the bottom
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[Unreleased]:"):
            lines[i] = f"[Unreleased]: https://github.com/doppelmarker/mb_appearance/compare/v{new_version}...HEAD"
            lines.insert(i + 1, f"[{new_version}]: https://github.com/doppelmarker/mb_appearance/compare/v{old_version}...v{new_version}")
            break
    
    changelog_file.write_text("\n".join(lines))


def run_git_command(command):
    """Run a git command and return output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Bump version for mb-app")
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git operations (commit and tag)"
    )
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        help="Skip CHANGELOG.md update"
    )
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="Skip README.md usage update"
    )
    args = parser.parse_args()
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Calculate new version
    new_version = bump_version(current_version, args.bump_type)
    print(f"New version: {new_version}")
    
    # Check for uncommitted changes
    if not args.no_git:
        status = run_git_command("git status --porcelain")
        if status:
            print("Error: Uncommitted changes detected. Please commit or stash them first.")
            sys.exit(1)
    
    # Update version file
    update_version_file(new_version)
    print(f"Updated appearance/__version__.py")
    
    # Update README usage section
    if not args.no_readme:
        if update_readme_usage():
            print("Updated README.md usage section")
        else:
            print("README.md usage section is already up to date")
    
    # Update CHANGELOG
    if not args.no_changelog:
        update_changelog(current_version, new_version, args.bump_type)
        print("Updated CHANGELOG.md")
    
    # Git operations
    if not args.no_git:
        # Add files
        run_git_command("git add appearance/__version__.py")
        if not args.no_changelog:
            run_git_command("git add CHANGELOG.md")
        if not args.no_readme:
            run_git_command("git add README.md")
        
        # Commit
        commit_message = f"Bump version from {current_version} to {new_version}"
        run_git_command(f'git commit -m "{commit_message}"')
        print(f"Created commit: {commit_message}")
        
        # Create tag
        tag_name = f"v{new_version}"
        run_git_command(f'git tag -a {tag_name} -m "Version {new_version}"')
        print(f"Created tag: {tag_name}")
        
        print("\nNext steps:")
        print(f"1. Review the changes: git show HEAD")
        print(f"2. Push changes: git push origin main")
        print(f"3. Push tag: git push origin {tag_name}")
        print(f"4. Create GitHub release from tag {tag_name}")
        print(f"5. Build and upload to PyPI: python setup.py sdist bdist_wheel && twine upload dist/*")
    else:
        print("\nChanges made (no git operations performed)")


if __name__ == "__main__":
    main()