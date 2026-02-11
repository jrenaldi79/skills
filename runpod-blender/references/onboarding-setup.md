# Onboarding: Blender MCP Setup Guide

Walk the user through installing Blender, the Blender MCP addon, and connecting it to their LLM application. This guide supports both **local rendering** and **cloud GPU rendering (RunPod)**.

**Important:** You are running commands on the user's LOCAL machine. Always use Desktop Commander (`execute_command`, `start_process`), Bash, or equivalent local shell tool — NOT a sandboxed container. Confirm with the user before installing software.

**Supported LLM clients:** Claude Desktop, ChatWise, and Claude Code. The onboarding flow detects which client is in use and configures accordingly.

---

## Table of Contents

1. [Pre-Flight: Detect OS, Client, and Environment](#1-pre-flight-detect-os-client-and-environment)
2. [Install Blender](#2-install-blender)
3. [Install Python 3.10+](#3-install-python-310)
4. [Install uv Package Manager](#4-install-uv-package-manager)
5. [Download the Blender Addon](#5-download-the-blender-addon)
6. [Configure the MCP Server](#6-configure-the-mcp-server)
7. [Install and Enable the Addon in Blender](#7-install-and-enable-the-addon-in-blender)
8. [Verify the Connection](#8-verify-the-connection)
9. [Cloud (RunPod) Prerequisites](#9-cloud-runpod-prerequisites)
10. [RunPod Workspace and Pod Setup](#10-runpod-workspace-and-pod-setup)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Pre-Flight: Detect OS, Client, and Environment

Three things must be determined before any installation: the operating system, the LLM client, and whether the user wants local or cloud rendering.

### 1a. Detect Operating System

```bash
# macOS
uname -s
# Expected: "Darwin"

# Windows (PowerShell)
$env:OS
# Expected: "Windows_NT"

# Linux
uname -s
# Expected: "Linux"
```

Also check system architecture (Intel vs ARM matters for Blender downloads):

```bash
# macOS
uname -m
# "arm64" = Apple Silicon, "x86_64" = Intel

# Windows PowerShell
$env:PROCESSOR_ARCHITECTURE
# "AMD64" = x86_64, "ARM64" = ARM
```

### 1b. Detect LLM Client Application

Determine whether the user is running **Claude Desktop**, **ChatWise**, or **Claude Code**. Probe for installed clients — check which application data directories exist.

#### macOS

```bash
# Check for Claude Desktop
ls -d ~/Library/Application\ Support/Claude 2>/dev/null && echo "FOUND: Claude Desktop"

# Check for ChatWise
ls -d ~/Library/Application\ Support/app.chatwise 2>/dev/null && echo "FOUND: ChatWise"

# Check for Claude Code
which claude 2>/dev/null && echo "FOUND: Claude Code"
```

#### Windows (PowerShell)

```powershell
# Check for Claude Desktop
if (Test-Path "$env:APPDATA\Claude") { Write-Output "FOUND: Claude Desktop" }

# Check for ChatWise
if (Test-Path "$env:APPDATA\app.chatwise") { Write-Output "FOUND: ChatWise" }

# Check for Claude Code
Get-Command claude -ErrorAction SilentlyContinue
```

#### Decision Logic

| Detection Result | Action |
|---|---|
| Only Claude Desktop found | Use Claude Desktop config path (Step 6A) |
| Only ChatWise found | Use ChatWise SQLite config path (Step 6B) |
| Only Claude Code found | Use Claude Code project config (Step 6C) |
| Multiple clients found | Ask the user which app they want to connect Blender to |
| None found | Ask the user which app they're using |

Store the detected client as a variable — it's referenced in Steps 6, 8, and 11.

**If the user tells you which client they're using, trust that over the filesystem detection.** Some users may have multiple clients installed but only want to configure one.

### 1c. Determine Rendering Environment

Ask the user: **"Are you rendering locally or on a cloud GPU (RunPod)?"**

| User says | Path |
|---|---|
| "Local", "my machine", "my GPU" | Follow Steps 2-8 only. Skip Steps 9-10. |
| "Cloud", "RunPod", "remote", "cloud GPU" | Follow Steps 2-8 for local MCP setup, then continue to Steps 9-10 for RunPod. |
| Unclear | Default to local. Cloud can be added later. |

**Note:** Even cloud users need a local MCP setup (Steps 2-6) because the MCP server runs locally and tunnels to the remote Blender instance.

---

## 2. Install Blender

Blender 3.0 or newer is required. **For cloud (RunPod) users:** Blender is pre-installed on the pod — this step is only needed if the user also wants a local Blender installation for previewing .blend files. Cloud users can skip to Step 3 if they only need the MCP connection.

### Check Existing Installation

```bash
# macOS / Linux
which blender || blender --version 2>/dev/null

# Windows PowerShell
Get-Command blender -ErrorAction SilentlyContinue
```

If Blender is found and version is >= 3.0, skip to Step 3.

### Install Blender

#### macOS (Homebrew)

```bash
# Install Homebrew if not present
which brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Blender
brew install --cask blender
```

#### Windows (winget)

```powershell
winget install BlenderFoundation.Blender
```

If winget is unavailable, direct the user to https://www.blender.org/download/ for manual installation.

#### Linux (snap)

```bash
sudo snap install blender --classic
```

### Verify Installation

```bash
blender --version
```

Confirm version is 3.0 or higher. On macOS, the binary may be at `/Applications/Blender.app/Contents/MacOS/Blender` — add it to PATH if `blender` is not found.

---

## 3. Install Python 3.10+

The Blender MCP server requires Python 3.10 or newer.

### Check Existing Installation

```bash
# macOS / Linux
python3 --version

# Windows
python --version
```

If Python >= 3.10 is found, skip to Step 4.

### Install Python

#### macOS

```bash
brew install python@3.12
```

#### Windows

```powershell
winget install Python.Python.3.12
```

After installation on Windows, restart the terminal session so Python is on PATH.

#### Linux

```bash
sudo apt update && sudo apt install python3.12 python3.12-venv
```

### Verify

```bash
python3 --version  # or 'python --version' on Windows
```

---

## 4. Install uv Package Manager

`uv` is required to run the Blender MCP server via `uvx`. This is the most common failure point — do NOT proceed without it.

### Check Existing Installation

```bash
uv --version
```

If found, skip to Step 5.

### Install uv

#### macOS

```bash
brew install uv
```

#### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, add uv to the user PATH on Windows:

```powershell
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

**Important:** The user may need to restart their terminal (and their LLM client) after this step for PATH changes to take effect.

#### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify

```bash
uv --version
```

---

## 5. Download the Blender Addon

The addon file (`addon.py`) creates the socket server inside Blender that the MCP connects to.

**For cloud (RunPod) users:** The addon is already installed on the pod via `pod_setup.sh`. This step is only needed if the user also has a local Blender installation.

```bash
# macOS / Linux
curl -L -o ~/Downloads/addon.py https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py

# Windows PowerShell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py" -OutFile "$env:USERPROFILE\Downloads\addon.py"
```

### Verify Download

```bash
# macOS / Linux
ls -la ~/Downloads/addon.py

# Windows
Get-Item "$env:USERPROFILE\Downloads\addon.py"
```

Confirm the file exists and is not empty (should be several KB, not 0 bytes or an HTML error page).

---

## 6. Configure the MCP Server

This is where the path diverges based on the LLM client detected in Step 1b.

- **Claude Desktop** -> Step 6A (JSON config file)
- **ChatWise** -> Step 6B (SQLite database)
- **Claude Code** -> Step 6C (project .mcp.json file)

---

### Step 6A: Claude Desktop Configuration

Claude Desktop uses a JSON config file to define MCP servers.

#### Locate the Config File

**macOS:**

```bash
CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
echo "Config path: $CONFIG_PATH"
mkdir -p "$(dirname "$CONFIG_PATH")"
cat "$CONFIG_PATH" 2>/dev/null || echo "No config file yet — will create one."
```

**Windows:**

```powershell
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
Write-Output "Config path: $configPath"
New-Item -ItemType Directory -Force -Path (Split-Path $configPath)
if (Test-Path $configPath) { Get-Content $configPath } else { Write-Output "No config file yet." }
```

#### Write the Config

If the config file is empty or doesn't exist, write the full config. If it already has other MCP servers, merge the `blender` entry into the existing `mcpServers` object — do NOT overwrite other servers.

**macOS / Linux — New Config:**

```bash
cat > "$CONFIG_PATH" << 'EOF'
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
EOF
```

**Windows — New Config:**

```powershell
$config = @'
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
'@
$config | Set-Content -Path $configPath -Encoding UTF8
```

**Windows — Alternative (cmd wrapper):**

Some Windows environments need the `cmd /c` wrapper. Use this variant if the standard config fails to connect:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": ["/c", "uvx", "blender-mcp"]
        }
    }
}
```

#### Optional: Disable Telemetry (Claude Desktop)

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"],
            "env": {
                "DISABLE_TELEMETRY": "true"
            }
        }
    }
}
```

#### Verify Config

```bash
# macOS / Linux
cat "$CONFIG_PATH" | python3 -m json.tool

# Windows
Get-Content $configPath | python -m json.tool
```

Confirm the JSON is valid and contains the `blender` server entry. Then skip to Step 7.

---

### Step 6B: ChatWise Configuration

ChatWise stores MCP server definitions as rows in a local SQLite database (`app.db`). Configuration is done via SQL commands, not a config file.

#### Locate the Database

**macOS:**

```bash
DB_PATH="$HOME/Library/Application Support/app.chatwise/app.db"
echo "Database path: $DB_PATH"
ls -la "$DB_PATH" 2>/dev/null || echo "ERROR: ChatWise database not found. Is ChatWise installed?"
```

**Windows:**

```powershell
$dbPath = "$env:APPDATA\app.chatwise\app.db"
Write-Output "Database path: $dbPath"
if (Test-Path $dbPath) { Get-Item $dbPath } else { Write-Output "ERROR: ChatWise database not found." }
```

If the database doesn't exist, ChatWise may not be installed or hasn't been launched yet. Ask the user to open ChatWise at least once to initialize the database, then retry.

#### Check for Existing Blender MCP Entry

Before inserting, check if a `blender` server already exists:

```bash
# macOS / Linux
sqlite3 "$DB_PATH" "SELECT name, configuration FROM tool WHERE name = 'blender';"
```

```powershell
# Windows (requires sqlite3 on PATH — see troubleshooting if not available)
sqlite3 "$dbPath" "SELECT name, configuration FROM tool WHERE name = 'blender';"
```

#### Insert New Blender MCP Server

If no existing entry is found, insert a new row:

**macOS / Linux:**

```bash
sqlite3 "$DB_PATH" "INSERT INTO tool (name, configuration) VALUES ('blender', '{\"type\":\"stdio\",\"command\":\"uvx blender-mcp\",\"env\":\"\",\"longRunning\":true}');"
```

**Windows:**

```powershell
sqlite3 "$dbPath" "INSERT INTO tool (name, configuration) VALUES ('blender', '{""type"":""stdio"",""command"":""uvx blender-mcp"",""env"":"""",""longRunning"":true}');"
```

#### Update Existing Blender MCP Entry

If an entry already exists and needs to be replaced or fixed:

```bash
sqlite3 "$DB_PATH" "UPDATE tool SET configuration = '{\"type\":\"stdio\",\"command\":\"uvx blender-mcp\",\"env\":\"\",\"longRunning\":true}' WHERE name = 'blender';"
```

#### Optional: Disable Telemetry (ChatWise)

To add the `DISABLE_TELEMETRY` environment variable, set it in the `env` field. Note that ChatWise stores env vars as a newline-separated string:

```bash
sqlite3 "$DB_PATH" "UPDATE tool SET configuration = '{\"type\":\"stdio\",\"command\":\"uvx blender-mcp\",\"env\":\"DISABLE_TELEMETRY=true\",\"longRunning\":true}' WHERE name = 'blender';"
```

#### Verify the Entry

```bash
sqlite3 "$DB_PATH" "SELECT name, configuration FROM tool WHERE name = 'blender';"
```

Confirm the output shows the blender server with correct `type`, `command`, and `longRunning` fields.

**Important:** After modifying the database, the user must **fully restart ChatWise** (quit and reopen) for changes to take effect in the active runtime.

#### SQLite Not Available on Windows

If `sqlite3` is not on the Windows PATH, use Python as a fallback:

```powershell
python -c @"
import sqlite3, json, os
db = os.path.join(os.environ['APPDATA'], 'app.chatwise', 'app.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
config = json.dumps({'type':'stdio','command':'uvx blender-mcp','env':'','longRunning':True})
# Check if entry exists
cur.execute("SELECT name FROM tool WHERE name = 'blender'")
if cur.fetchone():
    cur.execute("UPDATE tool SET configuration = ? WHERE name = 'blender'", (config,))
    print('Updated existing blender entry.')
else:
    cur.execute("INSERT INTO tool (name, configuration) VALUES ('blender', ?)", (config,))
    print('Inserted new blender entry.')
conn.commit()
conn.close()
"@
```

On macOS/Linux, the equivalent Python fallback:

```bash
python3 -c "
import sqlite3, json, os
db = os.path.expanduser('~/Library/Application Support/app.chatwise/app.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
config = json.dumps({'type':'stdio','command':'uvx blender-mcp','env':'','longRunning':True})
cur.execute(\"SELECT name FROM tool WHERE name = 'blender'\")
if cur.fetchone():
    cur.execute(\"UPDATE tool SET configuration = ? WHERE name = 'blender'\", (config,))
    print('Updated existing blender entry.')
else:
    cur.execute(\"INSERT INTO tool (name, configuration) VALUES ('blender', ?)\", (config,))
    print('Inserted new blender entry.')
conn.commit()
conn.close()
"
```

These Python scripts handle both insert and update safely, and avoid SQL escaping issues with the JSON payload.

---

### Step 6C: Claude Code Configuration

Claude Code uses a `.mcp.json` file in the project directory to define MCP servers.

#### Create the Config File

In your project working directory (e.g., `~/blender-files/runpod/`), create or update `.mcp.json`:

```bash
cat > ~/blender-files/runpod/.mcp.json << 'EOF'
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
EOF
```

**Windows:**

```powershell
$config = @'
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
'@
$config | Set-Content -Path ".mcp.json" -Encoding UTF8
```

If the file already has other MCP servers, merge the `blender` entry into the existing `mcpServers` object — do NOT overwrite other servers.

#### Verify Config

```bash
cat .mcp.json | python3 -m json.tool
```

Confirm the JSON is valid and contains the `blender` server entry. Claude Code will automatically detect `.mcp.json` in the project directory.

**Note:** No client restart is needed — Claude Code picks up `.mcp.json` changes when starting a new conversation in that directory.

---

## 7. Install and Enable the Addon in Blender

This step requires the user to interact with the Blender GUI. **Cloud (RunPod) users:** Skip this step — the addon is pre-installed on the pod and auto-starts via `/runpod/autostart_mcp.py`.

Walk local users through it:

1. **Open Blender.**
2. Go to **Edit -> Preferences -> Add-ons**.
3. Click **"Install..."** (top right).
4. Navigate to `~/Downloads/addon.py` (or `%USERPROFILE%\Downloads\addon.py` on Windows) and select it.
5. **Enable the addon** by checking the box next to **"Interface: Blender MCP"**.
6. The addon panel will appear in the **3D Viewport sidebar** (press `N` to toggle the sidebar if hidden).
7. Find the **"BlenderMCP"** tab in the sidebar.
8. Optionally check **"Poly Haven"** to enable HDRI/texture/model downloads.
9. Click **"Connect to Claude"** (this button label is the same regardless of which client — it starts the local socket server on port 9876).

Tell the user: *"Once you see 'Connected' in the BlenderMCP panel and the Blender MCP tools appear in your LLM client, you're ready to go."*

---

## 8. Verify the Connection

After the addon is running in Blender and the LLM client has been restarted:

### For Claude Desktop
- Check that Claude shows the **hammer icon** with Blender MCP tools available.

### For ChatWise
- Check that the Blender MCP server shows as active/connected in ChatWise's tool list.

### For Claude Code
- Start a new conversation in the project directory. Blender MCP tools should appear automatically.

### Smoke Test (All Clients)

Run a quick test to confirm two-way communication:

```
Call get_scene_info to verify the Blender connection is active.
```

If `get_scene_info` returns scene data (default cube, camera, light), the connection is working.

For a deeper verification:

```
Call execute_blender_code with: import bpy; print(bpy.app.version_string)
```

This should return the Blender version string.

**Local users:** Setup is complete. You're ready to render.

**Cloud (RunPod) users:** Continue to Step 9.

---

## 9. Cloud (RunPod) Prerequisites

These steps are only for users who want to render on a cloud GPU. Complete Steps 1-6 first (the local MCP server is still needed — it tunnels to the remote pod).

### 9a. Create a RunPod Account

1. Go to [runpod.io](https://runpod.io) and create an account.
2. **Add a payment method.** The user must do this themselves — Claude cannot enter financial information. Instruct them: go to **Settings -> Billing** and add a credit card or other payment method.
3. Add initial credits ($10-25 is sufficient for getting started).

### 9b. Generate a RunPod API Key

1. In RunPod, go to **Settings -> API Keys**.
2. Click **Create API Key**.
3. Copy the key (starts with `rpa_`). Store it securely — it won't be shown again.
4. This key will be saved to `.env` in Step 10.

### 9c. Set Up SSH Key

RunPod uses SSH keys for pod access. Install the RunPod CLI and generate a key:

```bash
# Install RunPod CLI
pip install runpodctl

# Generate SSH key (creates ~/.runpod/ssh/RunPod-Key-Go)
runpodctl ssh add-key
```

Verify the key exists:

```bash
ls -la ~/.runpod/ssh/RunPod-Key-Go
```

If the file exists, SSH key setup is complete. The key is automatically registered with your RunPod account.

**Troubleshooting:** If `runpodctl` is not found after install, ensure `~/.local/bin` is on your PATH. On macOS, you may need to restart the terminal.

---

## 10. RunPod Workspace and Pod Setup

### 10a. First-Time Workspace Setup

Create the local project directory structure:

```bash
mkdir -p ~/blender-files/runpod/projects
mkdir -p ~/blender-files/runpod/skill/scripts
```

Copy skill files into `~/blender-files/runpod/skill/` (SKILL.md, scripts/).

Initialize git:

```bash
cd ~/blender-files/runpod && git init
```

Create `.gitignore` (exclude `.env`, `.DS_Store`, `*.blend1`, `__pycache__/`).

Create `.env` from the template (`skill/.env.example`):
- Ask the user for their RunPod API key (from Step 9b)
- Write it to `~/blender-files/runpod/.env`
- Leave `RUNPOD_POD_ID` blank (filled after pod creation)

### 10b. First-Time Pod Setup

1. Read API key from `.env`
2. Create pod:
   ```
   python3 SKILL_DIR/scripts/runpod_manager.py create --env-file ~/blender-files/runpod/.env
   ```
3. Extract pod ID from JSON output
4. Save pod ID to `.env`: update `RUNPOD_POD_ID=<new_pod_id>`
5. Wait for SSH, then pipe setup script:
   ```
   ssh -o StrictHostKeyChecking=no -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT \
     < SKILL_DIR/scripts/pod_setup.sh
   ```
6. Commit initial setup:
   ```
   cd ~/blender-files/runpod && git add -A && git commit -m "Initial RunPod Blender setup"
   ```

After pod setup is complete, see `references/runpod-infrastructure.md` for session management (start, stop, file transfer).

---

## 11. Troubleshooting

### "Connection refused" or timeout

- Confirm the Blender addon shows "Connected" (not just enabled).
- **Claude Desktop:** Confirm the app was **restarted** after editing `claude_desktop_config.json`.
- **ChatWise:** Confirm the app was **fully restarted** (quit + reopen) after modifying the SQLite database.
- **Claude Code:** Start a new conversation in the project directory where `.mcp.json` lives.
- Check that no other application is using port 9876:

```bash
# macOS / Linux
lsof -i :9876

# Windows
netstat -ano | findstr :9876
```

- Only run one instance of the MCP server at a time. Do not have multiple clients trying to connect simultaneously.

### "uvx: command not found"

- uv was not installed or not on PATH.
- On Windows: restart the terminal after PATH changes.
- On macOS: ensure `brew install uv` completed, then try `which uv`.

### "blender-mcp" package not found

- Run `uvx blender-mcp` manually in a terminal to see the error output.
- May indicate a Python version issue — ensure Python >= 3.10.

### LLM client doesn't show Blender tools

- **Claude Desktop:** Check the developer console (Help -> Developer -> Toggle Developer Tools) for MCP errors. Try removing and re-adding the blender entry in the config JSON.
- **ChatWise:** Verify the database entry exists: `sqlite3 "$DB_PATH" "SELECT * FROM tool WHERE name = 'blender';"`. Ensure `longRunning` is `true` in the config JSON. Fully restart ChatWise.
- **Claude Code:** Verify `.mcp.json` is in the project directory (not a subdirectory). Run `cat .mcp.json | python3 -m json.tool` to check for JSON syntax errors.
- On Windows, try the `cmd /c` wrapper variant for the command field.

### ChatWise: "no such table: tool"

- ChatWise may not have been opened yet. Launch ChatWise at least once to initialize the database schema, then retry.
- The database path may be wrong — verify with `ls` or `Test-Path`.

### ChatWise: Entry exists but Blender doesn't connect

- Read back the config: `sqlite3 "$DB_PATH" "SELECT configuration FROM tool WHERE name = 'blender';"` and verify the JSON is valid (not double-escaped or malformed).
- If the JSON looks broken, delete and re-insert: `sqlite3 "$DB_PATH" "DELETE FROM tool WHERE name = 'blender';"` then re-run the insert command.

### Blender addon doesn't appear after install

- Ensure addon.py was downloaded completely (not a 404 HTML page).
- Check Blender's console (Window -> Toggle System Console on Windows) for error messages.
- Try Blender 4.0+ if using an older version.

### First command fails, subsequent ones work

This is a known issue with Blender MCP. The first command after connecting sometimes times out. Retry — it typically works on the second attempt.

### RunPod SSH key not found

- Verify `~/.runpod/ssh/RunPod-Key-Go` exists. If not, re-run `runpodctl ssh add-key`.
- Ensure `runpodctl` is installed: `pip install runpodctl`.
- The key must be registered with your RunPod account — check in RunPod Settings -> SSH Keys.

### RunPod pod won't start

- Verify your API key is correct in `.env`.
- Check your RunPod account balance — pods require sufficient credits.
- The requested GPU type may be unavailable. Try a different region or GPU in the RunPod dashboard.

---

## Setup Checklist

Use this to track progress. The **Local** column applies to all users; the **Cloud** column is only for RunPod users.

| Step | Local | Cloud |
|------|-------|-------|
| Detect OS (macOS / Windows / Linux) | Required | Required |
| Detect LLM client (Claude Desktop / ChatWise / Claude Code) | Required | Required |
| Choose environment (local / cloud) | Required | Required |
| Blender >= 3.0 installed | Required | Optional (pre-installed on pod) |
| Python >= 3.10 installed | Required | Required |
| uv package manager installed | Required | Required |
| addon.py downloaded | Required | Optional (pre-installed on pod) |
| MCP server configured (JSON / SQLite / .mcp.json) | Required | Required |
| Addon installed and enabled in Blender | Required | Skip (auto-starts on pod) |
| "Connect to Claude" clicked in Blender | Required | Skip (auto-starts on pod) |
| LLM client restarted | Required | Required |
| Smoke test passed (get_scene_info works) | Required | Required |
| RunPod account created | - | Required |
| RunPod API key generated | - | Required |
| SSH key set up (runpodctl) | - | Required |
| Local workspace created | - | Required |
| Pod created and setup script run | - | Required |
