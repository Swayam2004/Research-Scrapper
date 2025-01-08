#!/usr/bin/env python3
import os
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil


def calculate_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def segregate_files(source_dir):
    """Segregate files into unique and duplicate folders based on content."""
    # Create destination directories
    source_path = Path(source_dir)
    unique_dir = source_path / "unique_files"
    duplicate_dir = source_path / "duplicate_files"

    unique_dir.mkdir(exist_ok=True)
    duplicate_dir.mkdir(exist_ok=True)

    # Dictionary to store file hashes and their paths
    hash_dict = defaultdict(list)

    # Calculate hashes for all files
    print("Analyzing files...")
    for file_path in source_path.glob("*"):
        if (
            file_path.is_file() and file_path.name != ".DS_Store"
        ):  # Skip directories and system files
            file_hash = calculate_file_hash(file_path)
            hash_dict[file_hash].append(file_path)

    # Move files to appropriate directories
    print("\nMoving files...")
    for file_hash, file_paths in hash_dict.items():
        if len(file_paths) == 1:
            # Unique file
            dest = unique_dir / file_paths[0].name
            print(f"Moving unique file: {file_paths[0].name}")
            shutil.move(str(file_paths[0]), str(dest))
        else:
            # Duplicate files
            for i, file_path in enumerate(file_paths):
                # Add number suffix for duplicate files
                name_parts = file_path.stem, file_path.suffix
                if i == 0:
                    new_name = f"{name_parts[0]}{name_parts[1]}"
                else:
                    new_name = f"{name_parts[0]}_{i}{name_parts[1]}"

                dest = duplicate_dir / new_name
                print(f"Moving duplicate file: {file_path.name} -> {new_name}")
                shutil.move(str(file_path), str(dest))

    # Print summary
    unique_count = len(list(unique_dir.glob("*")))
    duplicate_count = len(list(duplicate_dir.glob("*")))
    print(f"\nSummary:")
    print(f"Unique files: {unique_count}")
    print(f"Duplicate files: {duplicate_count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <source_directory>")
        sys.exit(1)

    source_dir = sys.argv[1]
    if not os.path.isdir(source_dir):
        print(f"Error: '{source_dir}' is not a valid directory")
        sys.exit(1)

    segregate_files(source_dir)
