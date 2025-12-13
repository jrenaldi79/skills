---
name: windows-onboarding
description: Onboards new Windows users by adapting the system prompt to their machine. Use when setting up a new user on Windows, when someone needs their Claude assistant customized for their specific Windows paths and preferences, or when migrating the skills system to a new Windows machine. Collects user information (name, username, Google Drive preferences) and generates a personalized system prompt with correct Windows paths.
---

# Windows Onboarding

This skill helps onboard new Windows users by adapting the system prompt template to their specific machine configuration.

## What This Skill Does

1.  **Installs dependencies** - Automatically installs Chocolatey, Python, and Git
2.  **Collects user information** - Prompts for name, Windows username, and Google Drive preferences
3.  **Verifies Google Drive First** - Guides the user through a manual setup and then intelligently finds the correct path before proceeding.
4.  **Generates personalized system prompt** - Creates a `system_prompt.md` with the verified, correct Windows paths.
5.  **Saves configuration** - Stores `user_config.json` for reference and future updates.

## When to Use This Skill

-   Setting up Claude for a new Windows user
-   Migrating the skills system to a new Windows machine
-   Updating user configuration after username or path changes
-   Initial onboarding for anyone adopting the Local Skills & Automation system

## Quick Start

### Step 1: Install Dependencies (Required)

**IMPORTANT: Must run ChatWise as Administrator for this step.**

Run the dependency installation script to install Chocolatey, Python, and Git:

```powershell
cd C:\Users\{username}\skills\windows-onboarding\scripts
.\install_dependencies.ps1
```

### Step 2: Run the Adapter Script

**IMPORTANT: Must run ChatWise as Administrator for this step.**

The `adapt_prompt.py` script will interactively collect user information and guide you through the entire setup.

```bash
python scripts/adapt_prompt.py
```

**Correct Order of Operations:**

1.  **Collect User Info**: The script first asks for your name, username, and (optional) Google Drive email.
2.  **Verify Google Drive First**: If an email is provided, the script *immediately* begins the Google Drive setup and verification process. It will:
    *   Display manual installation instructions and the download link.
    *   Pause and wait for you to confirm (`[y/n]`) that you have completed the installation and sign-in.
3.  **Intelligently Find Path**: After your confirmation, a verification script runs to automatically find the correct Google Drive path on your system (e.g., `C:\Users\...` or a `G:\` drive).
4.  **Create Folder & Test File**: The script then creates the `Skill-Deliverables` folder in the correct location and writes a test file to confirm sync is working.
5.  **Generate Prompt Last**: Only *after* the Google Drive path has been successfully verified does the script generate the `system_prompt.md` and `user_config.json`, ensuring the paths written to them are 100% accurate.

This verify-first approach guarantees that your configuration files are generated correctly based on the actual, confirmed state of your system.

### Step 3: Create Directory Structure

The script will output the required local directories. Please ensure they are created:

```powershell
mkdir C:\Users\{username}\skills
mkdir C:\Users\{username}\skills\.tmp
mkdir C:\Users\{username}\skills\deliverables
```

## Files Included

**scripts/**

*   `install_dependencies.ps1` - Installs Chocolatey, Python, and Git (requires admin).
*   `adapt_prompt.py` - The main, interactive onboarding script.
*   `verify_gdrive.py` - The intelligent script for finding and verifying the Google Drive path.

**references/**

*   `gdrive_setup.md` - Detailed Google Drive installation guide for manual reference.
