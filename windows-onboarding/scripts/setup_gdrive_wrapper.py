#!/usr/bin/env python3
"""
Google Drive Setup Wrapper - Launches PowerShell automation script

This Python wrapper makes it easier to call the PowerShell automation
from the main onboarding workflow.
"""

import subprocess
import sys
from pathlib import Path


def check_windows():
    """Verify we're running on Windows."""
    if sys.platform != "win32":
        print("❌ This script only runs on Windows")
        return False
    return True


def check_admin():
    """Check if running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def run_powershell_setup(email=None, skills_path=None):
    """Execute the PowerShell setup script."""
    script_dir = Path(__file__).parent
    ps_script = script_dir / "setup_gdrive.ps1"
    
    if not ps_script.exists():
        print(f"❌ PowerShell script not found: {ps_script}")
        return False
    
    # Build PowerShell command
    cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)]
    
    if email:
        cmd.extend(["-UserEmail", email])
    
    if skills_path:
        cmd.extend(["-SkillsPath", skills_path])
    
    try:
        print("\n🚀 Launching Google Drive setup...\n")
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run PowerShell script: {e}")
        return False


def main():
    if not check_windows():
        sys.exit(1)
    
    if not check_admin():
        print("⚠️  This script requires Administrator privileges")
        print("\nOptions:")
        print("1. Right-click PowerShell and 'Run as Administrator'")
        print("2. Then run: python setup_gdrive_wrapper.py")
        print("\nOr run the PowerShell script directly:")
        print("   .\\scripts\\setup_gdrive.ps1")
        sys.exit(1)
    
    # Get optional parameters
    email = None
    skills_path = None
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        skills_path = sys.argv[2]
    
    success = run_powershell_setup(email, skills_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
