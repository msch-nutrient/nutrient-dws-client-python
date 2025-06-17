#!/usr/bin/env python3
"""Build the package for distribution."""

import subprocess
import sys
from pathlib import Path


def main():
    """Build the package."""
    root_dir = Path(__file__).parent.parent

    # Clean previous builds
    print("Cleaning previous builds...")
    for dir_name in ["dist", "build", "*.egg-info"]:
        subprocess.run(["rm", "-rf", str(root_dir / dir_name)])

    # Build the package
    print("Building package...")
    result = subprocess.run(
        [sys.executable, "-m", "build"], cwd=root_dir, capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Build failed:\n{result.stderr}")
        return 1

    print("Build successful!")
    print("\nBuilt files:")
    dist_dir = root_dir / "dist"
    for file in dist_dir.iterdir():
        print(f"  - {file.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
