# Google Drive Setup Guide for Windows

This guide walks through setting up Google Drive Desktop on Windows to sync your Skill-Deliverables folder.

## Prerequisites

- Windows 10 or 11
- Google account with Drive access
- Administrator access on your machine

## Setup Options

Choose your preferred setup method:

### Option A: Automated Setup (Recommended)

Run the PowerShell automation script that handles download, installation, and folder creation:

```powershell
# Run PowerShell as Administrator, then:
cd C:\Users\{YourUsername}\skills\windows-onboarding\scripts
.\setup_gdrive.ps1
```

Or use the Python wrapper:

```bash
python scripts\setup_gdrive_wrapper.py [email] [skills_path]
```

**What the script does automatically:**
- Downloads Google Drive for Desktop installer
- Installs silently with desktop shortcut
- Starts Google Drive service
- Creates Skill-Deliverables folder
- Creates test file to verify sync
- Updates user_config.json with correct path

**What you still need to do:**
- Sign in to Google account (OAuth browser flow - cannot be automated)
- Verify sync is working

### Option B: Manual Installation

If you prefer manual setup or the automated script fails, follow these steps:

## Manual Installation Steps

### 1. Download Google Drive for Desktop

1. Visit: https://www.google.com/drive/download/
2. Click "Download Drive for desktop"
3. Run the installer (GoogleDriveSetup.exe)
4. Follow the installation wizard

### 2. Sign In and Configure

1. After installation, Google Drive will open automatically
2. Click "Sign in with browser"
3. Sign in with your Google account
4. Choose sync option:
   - **Recommended**: "Mirror files" - Files exist both online and locally
   - Alternative: "Stream files" - Files stored in cloud, downloaded on-demand

### 3. Locate Your Google Drive Folder

By default, Google Drive creates a folder at:
```
C:\Users\{YourUsername}\Google Drive
```

Or if using the newer "My Drive" structure:
```
C:\Users\{YourUsername}\Google Drive\My Drive
```

### 4. Create Skill-Deliverables Folder

1. Open File Explorer
2. Navigate to your Google Drive folder
3. Create a new folder named `Skill-Deliverables`
4. This folder will now sync automatically

### 5. Verify Sync

1. Create a test file in the Skill-Deliverables folder
2. Check https://drive.google.com in your browser
3. Confirm the folder and test file appear online

## Configuration in System Prompt

The adapt_prompt.py script will set your Google Drive path to:
```
C:\Users\{YourUsername}\Google Drive\Skill-Deliverables
```

If you need to change this later, edit the generated `user_config.json` file and regenerate the system prompt.

## Common Issues

### Drive Icon Not Showing
- Check system tray (bottom-right corner)
- Click "Show hidden icons" arrow
- Google Drive icon should be there

### Folder Not Syncing
- Right-click the folder
- Select "Available offline" to force sync
- Check Google Drive settings (gear icon in systray)

### Wrong Drive Folder Location
- Open Google Drive preferences (systray icon > Settings)
- Check "Folder location" under "My Computer"
- Adjust path if needed

## Alternative: OneDrive or Dropbox

If you prefer different cloud storage:

**OneDrive** (pre-installed on Windows):
- Default location: `C:\Users\{YourUsername}\OneDrive`
- Create Skill-Deliverables folder there
- Update path in adapt_prompt.py before running

**Dropbox**:
- Default location: `C:\Users\{YourUsername}\Dropbox`
- Create Skill-Deliverables folder there  
- Update path in adapt_prompt.py before running

## Security Notes

- Skill deliverables may contain sensitive information
- Ensure your Google Drive has strong password and 2FA
- Consider using encrypted folders for highly sensitive work
- Review sharing permissions regularly
