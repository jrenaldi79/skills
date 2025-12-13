#!/usr/bin/env python3
"""
System Prompt Adapter - Customizes the system prompt for a new user's machine

This script prompts for user information and adapts the system prompt template
to work on their Windows machine with their specific paths and preferences.
"""

import os
import sys
from pathlib import Path
import json
import ctypes
import subprocess


def is_admin():
    """Check if script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_admin_privileges():
    """Verify script is running as administrator, exit with instructions if not"""
    if not is_admin():
        print("\n" + "="*60)
        print("ERROR: Administrator privileges required!")
        print("="*60)
        print("\nThis script requires administrator privileges to run properly.")
        print("\nTo run as administrator:")
        print("  1. Close this ChatWise window completely")
        print("  2. Open Task Manager (Ctrl+Shift+Esc)")
        print("  3. Kill all 'chatwise.exe' and 'node.exe' processes")
        print("  4. Double-click 'ChatWise (Admin)' shortcut on your desktop")
        print("  5. Click 'Yes' when UAC prompt appears")
        print("  6. Return to this conversation and run the script again")
        print("\n" + "="*60)
        sys.exit(1)
    else:
        print("[OK] Running with Administrator privileges\n")


SYSTEM_PROMPT_TEMPLATE = '''# Local Skills & Automation Assistant — System Prompt

## Identity
You are the Local Skills & Automation Assistant for {user_name}. Your job is to execute tasks by dynamically retrieving and using skills in the local environment. You must operate within the specified directories and follow strict pathing and storage protocols.

## Environment Configuration
- Skills Repository: {skills_path}
- Temporary Workspace: {tmp_path}
  - Python virtual environments MUST be created here (e.g., {tmp_path}\\venv)
- Deliverables: {deliverables_path}
- Google Drive (if explicitly requested): {gdrive_path}
- Always use backslashes (\\) in all paths for Windows.

## Skill Resolution Strategy
1) Match: Map the user's request to a skill by comparing intent to the Skills Registry descriptions.
2) Locate: Find the skill at {skills_path}
   - Single-file skill: skillname.md | .py | .sh
   - Directory skill: skillname/SKILL.md (always check directories if single file not found)
3) Analyze:
   - Instructional files (.md, .txt): Read and follow.
   - Executables (.py, .sh, .js): Inspect (or run with --help) to understand arguments; then execute with necessary inputs.

## Package Management (Windows)
- **Always use Chocolatey** for software installations on Windows
- Syntax: `choco install <package> -y`
- Common packages: git, python, nodejs, vscode, etc.
- Avoid winget or manual downloads unless Chocolatey doesn't have the package
- Check available packages: `choco search <package>`

## Operational Rules
- Dynamic Adaptation: Read the skill first. Never assume behavior without reading the skill.
- Path Safety: Verify directories exist before writing. Create them if missing (not system roots).
- Cleanliness: Use .tmp for all intermediate artifacts. Do not clutter /skills root.
- Deliverables: Place final outputs in {deliverables_path} and report the full path.
- Skill Management: When creating/updating a skill, use the skill-creator skill (scripts/init_skill.py and scripts/package_skill.py).
- Asset Handling:
  - Prefer stable URLs for external assets.
  - For robust deliverables, download to .tmp (via Python venv if needed) and embed/base64 as appropriate.

## Python Execution Protocol
- Never install packages globally.
- Create venv: python -m venv {tmp_path}\\venv
- Activate & install: {tmp_path}\\venv\\Scripts\\activate && pip install <libraries>
- Execute: {tmp_path}\\venv\\Scripts\\activate && python <script.py>

## File Writing Protocol
- Write files in single operations for most cases (0-150 lines)
- Only chunk files when they genuinely exceed 200+ lines
- Ignore performance notes suggesting chunking for files under 150 lines - they're just informational
- For 200+ line files: use chunks of ~75-100 lines each with mode='append'
- The chunking recommendation in tool descriptions is overly conservative - writing 100-150 line files in one go is more efficient

## Tool Use & Syntax (MCP) — CRITICAL HYGIENE
- Use only one tool per message.
- Place tool calls at end of message, top-level.
- Use absolute paths with backslashes for Windows.
- Keep JSON valid and compact.

## Default Response Style
- Be concise by default; expand only as needed.
- Use bullet points for clarity.
- Unless otherwise requested, respond in same language as user.
- When using the terminal tool, provide the user with quick updates when doing so so they know what is happening. One sentence updates are fine.

## Skills Registry (Full Metadata)
{skills_registry}
'''


def get_user_input():
    """Prompt user for their information."""
    print("\n=== Windows Onboarding Setup ===")
    print("This script will customize the system prompt for your machine.\n")
    
    user_name = input("Enter your full name: ").strip()
    if not user_name:
        print("Error: Name cannot be empty")
        sys.exit(1)
    
    username = input("Enter your Windows username (for C:\\Users\\...): ").strip()
    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)
    
    user_home = f"C:\\Users\\{username}"
    skills_path = f"{user_home}\\skills"
    tmp_path = f"{skills_path}\\.tmp"
    deliverables_path = f"{skills_path}\\deliverables"
    
    print("\nFor Google Drive integration (optional, press Enter to skip):")
    gdrive_email = input("Enter your Google Drive email: ").strip()
    
    if gdrive_email:
        gdrive_path = f"{user_home}\\Google Drive\\Skill-Deliverables"
    else:
        gdrive_path = "[Not configured - see references/gdrive_setup.md]"
    
    return {
        "user_name": user_name,
        "username": username,
        "skills_path": skills_path,
        "tmp_path": tmp_path,
        "deliverables_path": deliverables_path,
        "gdrive_email": gdrive_email,
        "gdrive_path": gdrive_path
    }


def scan_skills_registry(skills_path):
    """Scan skills directory and build registry from SKILL.md files."""
    registry_entries = []
    
    # Ensure skills path exists
    skills_dir = Path(skills_path)
    if not skills_dir.exists():
        return generate_skills_registry_placeholder()
        
    # Scan for skills
    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding='utf-8')
                    # Simple parsing of frontmatter
                    name = ""
                    description = ""
                    
                    if content.startswith("---"):
                        frontmatter = content.split("---")[1]
                        for line in frontmatter.splitlines():
                            if line.strip().startswith("name:"):
                                name = line.split(":", 1)[1].strip()
                            elif line.strip().startswith("description:"):
                                description = line.split(":", 1)[1].strip()
                    
                    if name:
                        entry = f"### {name}\n- **name:** {name}\n- **description:** {description or 'No description provided.'}"
                        registry_entries.append(entry)
                except Exception as e:
                    print(f"Warning: Failed to parse {skill_md}: {e}")
    
    if not registry_entries:
        return generate_skills_registry_placeholder()
        
    return "\n\n".join(sorted(registry_entries))


def generate_skills_registry_placeholder():
    return """### skill-creator
- **name:** skill-creator
- **description:** Guide for creating effective skills.

[Additional skills will be listed here as they are added]"""


def adapt_system_prompt(user_data):
    # Try to scan for existing skills, otherwise use placeholder
    try:
        skills_registry = scan_skills_registry(user_data["skills_path"])
    except Exception:
        skills_registry = generate_skills_registry_placeholder()
        
    return SYSTEM_PROMPT_TEMPLATE.format(
        user_name=user_data["user_name"],
        skills_path=user_data["skills_path"],
        tmp_path=user_data["tmp_path"],
        deliverables_path=user_data["deliverables_path"],
        gdrive_path=user_data["gdrive_path"],
        skills_registry=skills_registry
    )


def save_config(user_data, output_dir):
    config_path = Path(output_dir) / "user_config.json"
    with open(config_path, 'w') as f:
        json.dump(user_data, f, indent=2)
    return config_path

def handle_gdrive_setup(user_data):
    """Guides user through manual GDrive setup and returns the verified path."""
    print("\n=== Google Drive Setup Assistant ===")
    print("To sync your deliverables, please follow these manual setup steps:")
    print("\n1. Download and Install Google Drive for Desktop:")
    print("   - Go to: https://www.google.com/drive/download/")
    print("   - Run the installer and follow the on-screen instructions.")
    print("\n2. Sign In and Configure:")
    print("   - After installation, sign in with your Google account in the browser.")
    print(f"   - Ensure you are signed in as: {user_data['gdrive_email']}")
    print("   - Choose the 'Mirror files' option when prompted for best performance.")

    while True:
        confirm = input("\nHave you completed the download, installation, and sign-in? [y/n]: ").lower().strip()
        if confirm == 'y':
            break
        elif confirm == 'n':
            print("Aborting. Please complete the setup steps and run the script again.")
            sys.exit(0)
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    print("\n[VERIFYING] Attempting to locate Google Drive and verify setup...")
    
    verifier_script_path = Path(__file__).parent / "verify_gdrive.py"
    user_home = Path(user_data['skills_path']).parent
    
    try:
        result = subprocess.run(
            [sys.executable, str(verifier_script_path), str(user_home)],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        output_lines = result.stdout.strip().splitlines()
        verified_path = output_lines[-1]
        
        # Print all output except the last line (the path) for cleaner user display
        print("\n".join(output_lines[:-1]))
        
        print(f"\n[SUCCESS] Google Drive setup verified successfully!")
        print(f"      -> Confirmed Path: {verified_path}")
        return verified_path
        
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] Google Drive verification failed!")
        print("Please double-check the setup steps and try again.")
        print("Details from verifier:")
        if e.stdout:
            print("--- Output ---")
            print(e.stdout)
        if e.stderr:
            print("--- Error ---")
            print(e.stderr)
        sys.exit(1)
    except (FileNotFoundError, IndexError):
        print(f"\n[ERROR] Verification script failed or returned an unexpected value.")
        sys.exit(1)


def main():
    # Verify administrator privileges before proceeding
    check_admin_privileges()
    
    user_data = get_user_input()
    
    # If GDrive email is provided, handle setup and get the verified path BEFORE generating files
    if user_data["gdrive_email"]:
        verified_gdrive_path = handle_gdrive_setup(user_data)
        # Update user_data with the REAL path
        user_data["gdrive_path"] = verified_gdrive_path
    
    print("\n=== Generating System Prompt & Config Files ===")
    adapted_prompt = adapt_system_prompt(user_data)
    
    output_dir = Path.cwd()
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_path = output_dir / "system_prompt.md"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(adapted_prompt)
    
    config_path = save_config(user_data, output_dir)
    
    print(f"\n[SUCCESS] System prompt saved to: {prompt_path}")
    print(f"[SUCCESS] User config saved to: {config_path}")
    
    print(f"\n[ACTION] Please ensure these directories exist on your machine:")
    print(f"   - {user_data['skills_path']}")
    print(f"   - {user_data['tmp_path']}")
    print(f"   - {user_data['deliverables_path']}")

if __name__ == "__main__":
    main()
