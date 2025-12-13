# Windows Onboarding - Dependency Installation Script
# Installs Chocolatey, Python, and Git

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

# Function to refresh environment variables
function Refresh-Environment {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # If Chocolatey is installed, import its profile for proper env refresh
    if (Test-Path "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1") {
        Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1" -ErrorAction SilentlyContinue
        Update-SessionEnvironment -ErrorAction SilentlyContinue
    }
}
# Function to verify a command is available
function Test-CommandAvailable {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Check if Chocolatey is installed
Write-Host "Checking for Chocolatey..." -ForegroundColor Cyan
$chocoInstalled = Test-CommandAvailable "choco"

if ($chocoInstalled) {
    Write-Host "[OK] Chocolatey is already installed" -ForegroundColor Green
} else {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment to make choco available
        Refresh-Environment
        
        # Verify Chocolatey is now available
        if (Test-CommandAvailable "choco") {
            Write-Host "[OK] Chocolatey installed successfully" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Chocolatey installed but not available in PATH" -ForegroundColor Yellow
            Write-Host "You may need to restart your terminal" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERROR: Failed to install Chocolatey" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""

# Refresh environment variables after Chocolatey install
Refresh-Environment

# Check if Python is installed
Write-Host "Checking for Python..." -ForegroundColor Cyan
$pythonInstalled = Test-CommandAvailable "python"

if ($pythonInstalled) {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "[OK] Python is already installed: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Python found but version check failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Installing Python..." -ForegroundColor Yellow
    try {
        choco install python -y
        
        # Refresh environment to make python available
        Refresh-Environment
        
        # Verify Python is now available
        if (Test-CommandAvailable "python") {
            $pythonVersion = python --version 2>&1
            Write-Host "[OK] Python installed successfully: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Python installed but not available in PATH" -ForegroundColor Yellow
            Write-Host "You will need to restart your terminal" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERROR: Failed to install Python" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""

# Check if Git is installed
Write-Host "Checking for Git..." -ForegroundColor Cyan
$gitInstalled = Test-CommandAvailable "git"

if ($gitInstalled) {
    try {
        $gitVersion = git --version 2>&1
        Write-Host "[OK] Git is already installed: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Git found but version check failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        choco install git -y
        
        # Refresh environment to make git available
        Refresh-Environment
        
        # Verify Git is now available
        if (Test-CommandAvailable "git") {
            $gitVersion = git --version 2>&1
            Write-Host "[OK] Git installed successfully: $gitVersion" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Git installed but not available in PATH" -ForegroundColor Yellow
            Write-Host "You will need to restart your terminal" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERROR: Failed to install Git" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installed components:" -ForegroundColor Cyan
Write-Host "  [OK] Chocolatey package manager" -ForegroundColor Green
Write-Host "  [OK] Python 3.x" -ForegroundColor Green
Write-Host "  [OK] Git version control" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: You may need to close and reopen ChatWise for PATH changes to take effect." -ForegroundColor Yellow
Write-Host ""
pause