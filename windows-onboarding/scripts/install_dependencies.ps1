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

function Refresh-Environment {
    Write-Host "Refreshing environment variables..." -ForegroundColor DarkGray
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
        Refresh-Environment
    }
}

# --- INSTALLATION LOGIC ---

# 1. Chocolatey
Write-Host "Checking for Chocolatey..." -ForegroundColor Cyan
if (Test-CommandAvailable "choco") {
    Write-Host "[OK] Chocolatey is already installed" -ForegroundColor Green
} else {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Refresh-Environment
        
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

Refresh-Environment
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
        Refresh-Environment
        
        # Verify installation
        if (-not (Test-InstallationHealth "python" "Python \d+\.\d+\.\d+")) {
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
            Refresh-Environment
        }
        
        if (Test-InstallationHealth "python" "Python \d+\.\d+\.\d+") {
            $v = python --version 2>&1
            Write-Host "[OK] Python installed successfully: $v" -ForegroundColor Green
        } else {
            throw "Python installation failed both methods"
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
        Refresh-Environment
        
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
Write-Host "IMPORTANT: You may need to close and reopen ChatWise for PATH changes to take effect." -ForegroundColor Yellow
Write-Host ""
pause