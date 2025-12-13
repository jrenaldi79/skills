# Windows Onboarding - Dependency Installation Script
# Installs Chocolatey, Python, and Git with robust verification and fallbacks

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Onboarding - Dependency Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please close this window and run ChatWise using the 'ChatWise (Admin)' shortcut." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# --- HELPER FUNCTIONS ---

function Refresh-Path {
    Write-Host "Refreshing environment variables in current session..." -ForegroundColor DarkGray
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (Test-Path "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1") {
        Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1" -ErrorAction SilentlyContinue
        Update-SessionEnvironment -ErrorAction SilentlyContinue
    }
}

function Test-InstallationHealth {
    param([string]$Command, [string]$VersionPattern)
    
    # Level 1: Check if command exists
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $cmd) { return $false }
    
    # Level 2: Verify executable file exists
    if (-not (Test-Path $cmd.Source)) { return $false }
    
    # Level 3: Test actual execution
    try {
        $output = & $Command --version 2>&1
        if ($output -match $VersionPattern) {
            return $true
        }
    } catch {}
    
    return $false
}

function Cleanup-CorruptedInstall {
    param([string]$PackageName)
    Write-Host "Checking for corrupted $PackageName installation..." -ForegroundColor Yellow
    
    # Check for .ignore files which indicate failed Chocolatey installs
    $ignoreFiles = Get-ChildItem "C:\ProgramData\chocolatey\lib\$PackageName*" -Recurse -Filter "*.ignore" -ErrorAction SilentlyContinue
    
    if ($ignoreFiles) {
        Write-Host "[WARN] Detected corrupted $PackageName installation (found .ignore files). Cleaning up..." -ForegroundColor Yellow
        choco uninstall $PackageName -y --force
        choco uninstall "$PackageName.install" -y --force
        Start-Sleep -Seconds 2
        Refresh-Path
    }
}

# --- INSTALLATION LOGIC ---

# 1. Chocolatey
Write-Host "Checking for Chocolatey..." -ForegroundColor Cyan
if ($null -ne (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "[OK] Chocolatey is already installed" -ForegroundColor Green
} else {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Refresh-Path
        
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-Host "[OK] Chocolatey installed successfully" -ForegroundColor Green
        } else {
            throw "Chocolatey installed but not found in PATH"
        }
    } catch {
        Write-Host "ERROR: Failed to install Chocolatey" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        pause
        exit 1
    }
}

Refresh-Path
Write-Host ""

# 2. Python
Write-Host "Checking for Python..." -ForegroundColor Cyan
Cleanup-CorruptedInstall "python"

if (Test-InstallationHealth "python" "Python \d+\.\d+\.\d+") {
    $v = python --version 2>&1
    Write-Host "[OK] Python is working: $v" -ForegroundColor Green
} else {
    Write-Host "Installing Python..." -ForegroundColor Yellow
    try {
        choco install python -y --force
        Refresh-Path
        
        # Verify installation with retry loop
        $pythonWorks = $false
        $attempts = 0
        $maxAttempts = 3
        
        while (-not $pythonWorks -and $attempts -lt $maxAttempts) {
            Refresh-Path
            if (Test-InstallationHealth "python" "Python \d+\.\d+\.\d+") {
                $pythonWorks = $true
            } else {
                $attempts++
                if ($attempts -lt $maxAttempts) {
                    Write-Host "Verification attempt $attempts failed. Retrying..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 2
                }
            }
        }
        
        if (-not $pythonWorks) {
            Write-Host "[WARN] Chocolatey install failed verification. Attempting direct fallback..." -ForegroundColor Yellow
            
            # Fallback: Direct Download
            $installerUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
            $installerPath = "$env:TEMP\python-installer.exe"
            
            Write-Host "Downloading Python installer..." -ForegroundColor DarkGray
            Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
            
            Write-Host "Installing Python (this may take a minute)..." -ForegroundColor DarkGray
            Start-Process -FilePath $installerPath -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait
            Remove-Item $installerPath
            
            # Manually add to PATH if needed
            $pythonPath = "C:\Program Files\Python312"
            if (Test-Path $pythonPath) {
                $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
                if ($currentPath -notmatch "Python312") {
                    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$pythonPath;$pythonPath\Scripts", "Machine")
                }
            }
            Refresh-Path
        }
        
        if (Test-InstallationHealth "python" "Python \d+\.\d+\.\d+") {
            $v = python --version 2>&1
            Write-Host "[OK] Python installed successfully: $v" -ForegroundColor Green
        } else {
            # Check if it works with full path as last resort
            $fullPath = "C:\Program Files\Python312\python.exe"
            if (Test-Path $fullPath) {
                 try {
                    $v = & $fullPath --version 2>&1
                    if ($v -match "Python \d+\.\d+\.\d+") {
                        Write-Host "[WARNING] Python works with full path but not via PATH" -ForegroundColor Yellow
                        Write-Host "[WARNING] You'll need to restart ChatWise for PATH to work" -ForegroundColor Yellow
                    } else {
                        throw "Python installation failed both methods"
                    }
                 } catch {
                     throw "Python installation failed both methods"
                 }
            } else {
                throw "Python installation failed both methods"
            }
        }
    } catch {
        Write-Host "ERROR: Failed to install Python" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        
        # Diagnostics
        Write-Host "`nDIAGNOSTICS:" -ForegroundColor Yellow
        Write-Host "PATH: $env:Path" -ForegroundColor DarkGray
        Get-ChildItem "C:\ProgramData\chocolatey\lib\python*" -Recurse -Filter "*.ignore" | ForEach-Object { Write-Host "Found ignored file: $_.FullName" -ForegroundColor Red }
    }
}

Write-Host ""

# 3. Git
Write-Host "Checking for Git..." -ForegroundColor Cyan
Cleanup-CorruptedInstall "git"

if (Test-InstallationHealth "git" "git version") {
    $v = git --version 2>&1
    Write-Host "[OK] Git is working: $v" -ForegroundColor Green
} else {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        choco install git -y --force
        Refresh-Path
        
        if (Test-InstallationHealth "git" "git version") {
            $v = git --version 2>&1
            Write-Host "[OK] Git installed successfully: $v" -ForegroundColor Green
        } else {
            throw "Git installed but failed verification"
        }
    } catch {
        Write-Host "ERROR: Failed to install Git" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Final Status:" -ForegroundColor Cyan

if (Test-InstallationHealth "choco" "Chocolatey") { Write-Host "  [OK] Chocolatey" -ForegroundColor Green } else { Write-Host "  [FAIL] Chocolatey" -ForegroundColor Red }
if (Test-InstallationHealth "python" "Python") { Write-Host "  [OK] Python" -ForegroundColor Green } else { Write-Host "  [FAIL] Python" -ForegroundColor Red }
if (Test-InstallationHealth "git" "git version") { Write-Host "  [OK] Git" -ForegroundColor Green } else { Write-Host "  [FAIL] Git" -ForegroundColor Red }

Write-Host ""
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host "IMPORTANT: ChatWise Restart Required" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "To ensure Python and Git are accessible in future sessions:" -ForegroundColor White
Write-Host ""
Write-Host "1. Close this ChatWise window completely" -ForegroundColor White
Write-Host "2. Press Ctrl+Shift+Esc to open Task Manager" -ForegroundColor White
Write-Host "3. End all 'chatwise.exe' processes" -ForegroundColor White
Write-Host "4. Double-click 'ChatWise (Admin)' shortcut on your desktop" -ForegroundColor White
Write-Host "5. Click 'Yes' when UAC prompt appears" -ForegroundColor White
Write-Host "6. Return to this conversation" -ForegroundColor White
Write-Host ""
Write-Host "After restarting, Python and Git will be available in all new sessions." -ForegroundColor Green
Write-Host ""
pause