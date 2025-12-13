# Google Drive for Desktop - Automated Setup Script
# Requires: Administrator privileges, Internet connection
# User interaction needed: Sign in to Google account (OAuth)

param(
    [string]$UserEmail = "",
    [string]$SkillsPath = "$env:USERPROFILE\skills"
)

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "\n=== Google Drive for Desktop - Automated Setup ===\n" -ForegroundColor Cyan

# Step 1: Download Google Drive installer
Write-Host "[1/5] Downloading Google Drive for Desktop..." -ForegroundColor Green
$installerUrl = "https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe"
$installerPath = "$env:TEMP\GoogleDriveSetup.exe"

try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "      ✅ Downloaded to: $installerPath" -ForegroundColor Gray
} catch {
    Write-Host "      ❌ Download failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Install Google Drive silently
Write-Host "\n[2/5] Installing Google Drive for Desktop (silent)..." -ForegroundColor Green
try {
    $process = Start-Process -FilePath $installerPath -ArgumentList "--silent", "--desktop_shortcut" -Wait -PassThru
    if ($process.ExitCode -eq 0) {
        Write-Host "      ✅ Installation complete" -ForegroundColor Gray
    } else {
        Write-Host "      ⚠️  Installation exit code: $($process.ExitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ❌ Installation failed: $_" -ForegroundColor Red
    exit 1
}

# Clean up installer
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

# Step 3: Wait for Google Drive to start
Write-Host "\n[3/5] Waiting for Google Drive to initialize..." -ForegroundColor Green
Start-Sleep -Seconds 5

# Try to find and start Google Drive if not running
$gdrivePath = "$env:ProgramFiles\Google\Drive File Stream\launch.bat"
if (Test-Path $gdrivePath) {
    $gdriveProcess = Get-Process "GoogleDriveFS" -ErrorAction SilentlyContinue
    if (-not $gdriveProcess) {
        Write-Host "      Starting Google Drive..." -ForegroundColor Gray
        Start-Process $gdrivePath
        Start-Sleep -Seconds 3
    }
    Write-Host "      ✅ Google Drive is running" -ForegroundColor Gray
} else {
    Write-Host "      ⚠️  Google Drive executable not found at expected location" -ForegroundColor Yellow
}

# Step 4: User sign-in (cannot be automated due to OAuth)
Write-Host "\n[4/5] User authentication required" -ForegroundColor Green
Write-Host "      ⚠️  You need to sign in to your Google account" -ForegroundColor Yellow
Write-Host "      1. Look for the Google Drive icon in your system tray (bottom-right)" -ForegroundColor Gray
Write-Host "      2. Click it and select 'Sign in with browser'" -ForegroundColor Gray
Write-Host "      3. Complete the sign-in process in your browser" -ForegroundColor Gray
Write-Host "\n      Press Enter after you've signed in successfully..." -ForegroundColor Cyan
Read-Host

# Step 5: Create Skill-Deliverables folder
Write-Host "\n[5/5] Setting up Skill-Deliverables folder..." -ForegroundColor Green

# Detect Google Drive path
$possiblePaths = @(
    "$env:USERPROFILE\Google Drive\My Drive",
    "$env:USERPROFILE\Google Drive",
    "G:\My Drive",
    "G:\"
)

$gdrivePath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $gdrivePath = $path
        Write-Host "      ✅ Found Google Drive at: $gdrivePath" -ForegroundColor Gray
        break
    }
}

if (-not $gdrivePath) {
    Write-Host "      ❌ Could not locate Google Drive folder" -ForegroundColor Red
    Write-Host "      Please create 'Skill-Deliverables' folder manually" -ForegroundColor Yellow
} else {
    # Create Skill-Deliverables folder
    $skillDeliverablesPath = Join-Path $gdrivePath "Skill-Deliverables"
    
    if (-not (Test-Path $skillDeliverablesPath)) {
        New-Item -ItemType Directory -Path $skillDeliverablesPath -Force | Out-Null
        Write-Host "      ✅ Created: $skillDeliverablesPath" -ForegroundColor Gray
    } else {
        Write-Host "      ✅ Already exists: $skillDeliverablesPath" -ForegroundColor Gray
    }
    
    # Create test file to verify sync
    $testFile = Join-Path $skillDeliverablesPath "_sync_test.txt"
    "Google Drive sync test - $(Get-Date)" | Out-File -FilePath $testFile -Encoding UTF8
    Write-Host "      ✅ Created test file: $testFile" -ForegroundColor Gray
    
    # Update user config if it exists
    $configPath = Join-Path $SkillsPath "user_config.json"
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath | ConvertFrom-Json
            $config.gdrive_path = $skillDeliverablesPath
            if ($UserEmail) {
                $config.gdrive_email = $UserEmail
            }
            $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
            Write-Host "      ✅ Updated user_config.json with Google Drive path" -ForegroundColor Gray
        } catch {
            Write-Host "      ⚠️  Could not update config: $_" -ForegroundColor Yellow
        }
    }
}

# Final instructions
Write-Host "\n=== Setup Complete! ===\n" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Verify sync is working:" -ForegroundColor Gray
Write-Host "   - Check https://drive.google.com in your browser" -ForegroundColor Gray
Write-Host "   - Look for the Skill-Deliverables folder" -ForegroundColor Gray
Write-Host "   - Confirm _sync_test.txt appears online" -ForegroundColor Gray
Write-Host "\n2. If sync isn't working:" -ForegroundColor Gray
Write-Host "   - Right-click the Google Drive folder" -ForegroundColor Gray
Write-Host "   - Select 'Make available offline'" -ForegroundColor Gray
Write-Host "\n3. Google Drive path for system prompt:" -ForegroundColor Gray
if ($gdrivePath) {
    Write-Host "   $skillDeliverablesPath" -ForegroundColor Yellow
}

Write-Host "\nPress Enter to exit..." -ForegroundColor Cyan
Read-Host
