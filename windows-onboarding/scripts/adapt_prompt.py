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
        print("✓ Running with Administrator privileges\n")


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


def generate_skills_registry_placeholder():
    return """### skill-creator
- **name:** skill-creator
- **description:** Guide for creating effective skills.

[Additional skills will be listed here as they are added]"""


def adapt_system_prompt(user_data):
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


def main():
    # Verify administrator privileges before proceeding
    check_admin_privileges()
    
    user_data = get_user_input()
    
    print("\n=== Generating System Prompt ===")
    adapted_prompt = adapt_system_prompt(user_data)
    
    output_dir = Path.cwd()
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_path = output_dir / "system_prompt.md"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(adapted_prompt)
    
    config_path = save_config(user_data, output_dir)
    
    print(f"\n✅ System prompt saved to: {prompt_path}")
    print(f"✅ User config saved to: {config_path}")
    
    if user_data["gdrive_email"]:
        print(f"\n⚠️  Next step: Set up Google Drive sync")
        print(f"   See: references/gdrive_setup.md")
    
    print(f"\n📁 Create these directories on your machine:")
    print(f"   - {user_data['skills_path']}")
    print(f"   - {user_data['tmp_path']}")
    print(f"   - {user_data['deliverables_path']}")

if __name__ == "__main__":
    main()
