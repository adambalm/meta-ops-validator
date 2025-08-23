#!/usr/bin/env python3
"""
Code formatting script for MetaOps Validator.
Enforces consistent formatting and trailing newlines.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set


def get_python_files(directory: Path) -> List[Path]:
    """Get all Python files in the directory recursively."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__', '.git', '.pytest_cache', 'node_modules'}]

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files


def ensure_trailing_newline(file_path: Path) -> bool:
    """Ensure file ends with a trailing newline."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        if not content:
            return False

        # Check if file ends with newline
        if not content.endswith(b'\n'):
            with open(file_path, 'ab') as f:
                f.write(b'\n')
            print(f"Added trailing newline to {file_path}")
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return False


def format_with_black(file_path: Path) -> bool:
    """Format Python file with black."""
    try:
        result = subprocess.run(
            ['python', '-m', 'black', '--line-length', '100', '--quiet', str(file_path)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("Warning: black not installed. Install with: pip install black")
        return False


def remove_trailing_whitespace(file_path: Path) -> bool:
    """Remove trailing whitespace from lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        cleaned_lines = []

        for line in lines:
            cleaned_line = line.rstrip() + '\n' if line.strip() else '\n'
            if cleaned_line != line:
                modified = True
            cleaned_lines.append(cleaned_line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"Removed trailing whitespace from {file_path}")

        return modified
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def check_imports_order(file_path: Path) -> bool:
    """Check if imports are properly ordered (using isort if available)."""
    try:
        result = subprocess.run(
            ['python', '-m', 'isort', '--check-only', '--quiet', str(file_path)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # Try to fix automatically
            subprocess.run(['python', '-m', 'isort', str(file_path)], capture_output=True)
            print(f"Fixed import order in {file_path}")
            return True
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main formatting script."""
    project_root = Path(__file__).parent.parent

    print("🔧 Starting code formatting...")
    print(f"Project root: {project_root}")

    # Get all Python files
    python_files = get_python_files(project_root / "src")
    python_files.extend(get_python_files(project_root / "tests"))
    python_files.extend(get_python_files(project_root / "scripts"))

    print(f"Found {len(python_files)} Python files")

    # Track changes
    files_modified = set()

    # Format each file
    for file_path in python_files:
        print(f"Processing {file_path.relative_to(project_root)}...")

        # Remove trailing whitespace
        if remove_trailing_whitespace(file_path):
            files_modified.add(file_path)

        # Ensure trailing newline
        if ensure_trailing_newline(file_path):
            files_modified.add(file_path)

        # Format with black (if available)
        if format_with_black(file_path):
            files_modified.add(file_path)

        # Fix import order (if isort available)
        if check_imports_order(file_path):
            files_modified.add(file_path)

    print(f"\n✅ Formatting complete!")
    print(f"Modified {len(files_modified)} files:")
    for file_path in sorted(files_modified):
        print(f"  - {file_path.relative_to(project_root)}")

    # Check specific configuration files for trailing newlines
    config_files = [
        project_root / ".editorconfig",
        project_root / "requirements.txt",
        project_root / "CLAUDE.md",
        project_root / "README.md",
    ]

    print(f"\n🔧 Checking configuration files...")
    for config_file in config_files:
        if config_file.exists():
            if ensure_trailing_newline(config_file):
                print(f"Fixed trailing newline in {config_file.name}")

    print(f"\n🎉 All done! Code formatting enforced across {len(python_files)} Python files.")


if __name__ == "__main__":
    main()
