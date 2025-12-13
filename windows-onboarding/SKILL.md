---
name: windows-onboarding
description: Onboards new Windows users by adapting the system prompt to their machine. Use when setting up a new user on Windows, when someone needs their Claude assistant customized for their specific Windows paths and preferences, or when migrating the skills system to a new Windows machine. Collects user information (name, username, Google Drive preferences) and generates a personalized system prompt with correct Windows paths.
---

# Windows Onboarding

This skill helps onboard new Windows users by adapting the system prompt template to their specific machine configuration.

## What This Skill Does

1. **Installs dependencies** - Automatically installs Chocolatey, Python, and Git
2. **Collects user information** - Prompts for name, Windows username, and Google Drive preferences
3. **Generates personalized system prompt** - Creates a system_prompt.md with correct Windows paths
4. **Saves configuration** - Stores user_config.json for reference and future updates
5. **Guides Google Drive setup** - Provides detailed instructions for cloud sync (optional)

## When to Use This Skill

- Setting up Claude for a new Windows user
- Migrating the skills system to a new Windows machine
- Updating user configuration after username or path changes
- Initial onboarding for anyone adopting the Local Skills & Automation system

## Quick Start

### Step 1: Install Dependencies (Required)

**IMPORTANT: Must run ChatWise as Administrator for this step.**

Run the dependency installation script to install Chocolatey, Python, and Git:

```powershell
cd C:\Users\{username}\skills\windows-onboarding\scripts
.\install_dependencies.ps1
```

The script will:
- Verify you're running as Administrator
- Install Chocolatey package manager (if not present)
- Install Python 3.x (if not present)
- Install Git (if not present)

After installation completes, you may need to close and reopen ChatWise for PATH changes to take effect.

### Step 2: Run the Adapter Script

**IMPORTANT: Must run ChatWise as Administrator for this step.**

The `adapt_prompt.py` script will interactively collect user information:

```bash
python scripts/adapt_prompt.py
```

The script will:
- Verify you're running as Administrator (exits with instructions if not)
- Prompt for:
  - **Full name**: User's display name (e.g., "Sarah Johnson")
  - **Windows username**: System username for paths (e.g., "sjohnson")
  - **Google Drive email**: Optional, for cloud sync setup

If the script exits with an admin privileges error:
1. Close ChatWise completely
2. Open Task Manager (Ctrl+Shift+Esc)
3. Kill all 'chatwise.exe' and 'node.exe' processes
4. Double-click 'ChatWise (Admin)' shortcut on your desktop
5. Run the script again

Output files:
- `system_prompt.md` - Customized system prompt for Claude
- `user_config.json` - User configuration for reference

### Step 3: Create Directory Structure

The script outputs the required directories. Create them on the Windows machine:

```powershell
mkdir C:\Users\{username}\skills
mkdir C:\Users\{username}\skills\.tmp
mkdir C:\Users\{username}\skills\deliverables
```

### Step 4: Set Up Google Drive (Optional)

The script now follows a robust, verify-first workflow to ensure accuracy.

**Correct Order of Operations:**
1.  **Collect User Info**: The script first asks for your name, username, and (optional) Google Drive email.
2.  **Verify Google Drive First**: If an email is provided, the script *immediately* begins the Google Drive setup and verification process. It will:
    - Display manual installation instructions and the download link.
    - Pause and wait for you to confirm (`[y/n]`) that you have completed the installation and sign-in.
3.  **Intelligently Find Path**: After your confirmation, a verification script runs to automatically find the correct Google Drive path on your system (e.g., `C:\Users\...` or a `G:\` drive).
4.  **Create Folder & Test File**: The script then creates the `Skill-Deliverables` folder in the correct location and writes a test file to confirm sync is working.
5.  **Generate Prompt Last**: Only *after* the Google Drive path has been successfully verified does the script generate the `system_prompt.md` and `user_config.json`, ensuring the paths written to them are 100% accurate.

This verify-first approach guarantees that your configuration files are generated correctly based on the actual, confirmed state of your system.

### Step 5: Install Skills

Transfer skill files to the new machine:
- Copy skills to: `C:\Users\{username}\skills\`
- Ensure skill-creator skill is present
- Verify all skill SKILL.md files are readable

### Step 6: Apply System Prompt

Provide the generated `system_prompt.md` to Claude through the appropriate configuration method for the interface being used.

## Key Differences: Windows vs macOS

The adapter script automatically adjusts for Windows:

**Path Separators**:
- macOS: Forward slashes `/`
- Windows: Backslashes `\`

**Python Virtual Environments**:
- macOS: `venv/bin/activate`
- Windows: `venv\Scripts\activate`

**Default Paths**:
- macOS: `/Users/username/skills/`
- Windows: `C:\Users\username\skills\`

**File Creation**:
- macOS: `echo | base64 -d`
- Windows: `[System.IO.File]::WriteAllBytes()`

## Customization Options

### Change Default Paths

Edit `scripts/adapt_prompt.py` before running to change default locations:

```python
skills_path = f"{user_home}\\skills"  # Change base location
tmp_path = f"{skills_path}\\.tmp"       # Change temp location
```

### Update Existing Configuration

To regenerate the system prompt after changes:

1. Edit `user_config.json` with new values
2. Run: `python scripts/adapt_prompt.py`
3. Script will use existing config or prompt for updates

### Add Custom Skills to Registry

The generated system prompt includes a placeholder skills registry. To add your skills:

1. Open generated `system_prompt.md`
2. Locate the `## Skills Registry (Full Metadata)` section
3. Add skill entries following the format:

```markdown
### skill-name
- **name:** skill-name
- **description:** What the skill does and when to use it
```

## Troubleshooting

### Dependency Installation Fails
- Must run ChatWise as Administrator (use "ChatWise (Admin)" shortcut)
- Check internet connection for Chocolatey downloads
- If Chocolatey fails, try installing manually from https://chocolatey.org/install
- After installation, close and reopen ChatWise to refresh PATH

### Script Fails to Run
- Ensure Python 3.7+ is installed (run Step 1 first)
- Check PATH includes Python
- Run from correct directory

### Invalid Username
- Username must match Windows account name exactly
- Check: `echo %USERNAME%` in cmd
- Or: `$env:USERNAME` in PowerShell

### Google Drive Path Issues
- Default location: `C:\Users\{username}\Google Drive`
- Newer installs: `C:\Users\{username}\Google Drive\My Drive`
- Check actual location in Google Drive settings

### Paths Not Working
- Verify backslashes are correct (`\` not `/`)
- Ensure no trailing backslashes in paths
- Check for typos in username

## Files Included

**scripts/**
- `install_dependencies.ps1` - Installs Chocolatey, Python, and Git (requires admin)
- `adapt_prompt.py` - Main onboarding script that generates personalized system prompt
- `setup_gdrive.ps1` - PowerShell automation for Google Drive installation and setup
- `setup_gdrive_wrapper.py` - Python wrapper to launch PowerShell script with admin checks

**references/**
- `gdrive_setup.md` - Detailed Google Drive installation guide (automated + manual options)

## Next Steps After Onboarding

1. **Test the setup** - Ask Claude to create a simple file in deliverables
2. **Install more skills** - Use skill-creator to add domain-specific skills
3. **Configure MCP tools** - Set up any additional tools or integrations
4. **Share skills** - Package and distribute skills to team members
