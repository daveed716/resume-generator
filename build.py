#!/usr/bin/env python3
"""Build script — run on native Windows Python (not WSL) to create the executable."""

import os
import subprocess
import sys


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(base_dir, "app.spec")

    if not os.path.isfile(spec_file):
        print(f"Error: {spec_file} not found.")
        sys.exit(1)

    print("Building with PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--noconfirm"],
        cwd=base_dir,
    )

    if result.returncode == 0:
        print("\nBuild successful!")
        dist_dir = os.path.join(base_dir, "dist", "ResumeGenerator")
        print(f"Output: {dist_dir}")
    else:
        print("\nBuild failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
