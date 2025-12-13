#!/usr/bin/env python3
"""
Google Drive Setup Verifier - v2 (Intelligent Path Detection)

This script intelligently locates the Google Drive folder, creates the
Skill-Deliverables directory if it doesn't exist, and writes a test file.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def find_gdrive_path(user_home):
    """Search for the Google Drive directory in common locations."""
    user_home_path = Path(user_home)
    
    possible_paths = [
        user_home_path / "Google Drive",
        Path("G:/"),
        Path("F:/"),
        Path("H:/")
    ]
    
    print("Searching for Google Drive directory...")
    for path in possible_paths:
        # Check for a common marker file or directory
        if (path / "My Drive").exists():
            print(f"Found Google Drive at: {path / 'My Drive'}")
            return path / "My Drive"
        if path.exists() and any(item.name.startswith('.drive') for item in path.iterdir()):
             print(f"Found Google Drive at: {path}")
             return path

    # Fallback for the most common path if no markers are found
    if possible_paths[0].exists():
        print(f"Found Google Drive at: {possible_paths[0]}")
        return possible_paths[0]

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_gdrive.py <user_home_path>", file=sys.stderr)
        sys.exit(1)

    user_home = sys.argv[1]
    gdrive_base_path = find_gdrive_path(user_home)

    if not gdrive_base_path:
        print("Error: Could not automatically locate the Google Drive directory.", file=sys.stderr)
        print("Please ensure Google Drive for Desktop is installed, running, and you are signed in.", file=sys.stderr)
        sys.exit(1)

    skill_deliverables_path = gdrive_base_path / "Skill-Deliverables"
    print(f"Target deliverables path: {skill_deliverables_path}")

    try:
        print("Ensuring 'Skill-Deliverables' directory exists...")
        os.makedirs(skill_deliverables_path, exist_ok=True)
        print("Directory confirmed.")
    except Exception as e:
        print(f"Error: Failed to create directory at '{skill_deliverables_path}'.", file=sys.stderr)
        print(f"Please check your folder permissions. Details: {e}", file=sys.stderr)
        sys.exit(1)

    print("Attempting to create a test file...")
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        test_file_path = skill_deliverables_path / f"gdrive_sync_test_{timestamp}.txt"
        
        with open(test_file_path, 'w') as f:
            f.write(f"This is a test file created at {timestamp} to verify Google Drive sync.")
        
        print(f"Successfully created test file: {test_file_path}")
        print("Please check your Google Drive online to confirm the file has synced.")
        # Print the final path to stdout so the calling script can capture it
        print(skill_deliverables_path)

    except Exception as e:
        print(f"Error: Failed to create test file in '{skill_deliverables_path}'.", file=sys.stderr)
        print(f"Please check your folder permissions. Details: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
