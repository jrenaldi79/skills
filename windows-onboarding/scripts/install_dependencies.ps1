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

Write-Host "✓ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Check if Chocolatey is installed
Write-Host "Checking for Chocolatey..." -ForegroundColor Cyan
$chocoInstalled = $null -ne (Get-Command choco -ErrorAction SilentlyContinue)

if ($chocoInstalled) {
    Write-Host "✓ Chocolatey is already installed" -ForegroundColor Green
} else {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "✓ Chocolatey installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install Chocolatey" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Check if Python is installed
Write-Host "Checking for Python..." -ForegroundColor Cyan
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)

if ($pythonInstalled) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python is already installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Installing Python..." -ForegroundColor Yellow
    try {
        choco install python -y
        Write-Host "✓ Python installed successfully" -ForegroundColor Green
        # Refresh PATH after Python installation
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
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
$gitInstalled = $null -ne (Get-Command git -ErrorAction SilentlyContinue)

if ($gitInstalled) {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git is already installed: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        choco install git -y
        Write-Host "✓ Git installed successfully" -ForegroundColor Green
        # Refresh PATH after Git installation
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
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
Write-Host "  ✓ Chocolatey package manager" -ForegroundColor Green
Write-Host "  ✓ Python 3.x" -ForegroundColor Green
Write-Host "  ✓ Git version control" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: You may need to close and reopen ChatWise for PATH changes to take effect." -ForegroundColor Yellow
Write-Host ""
pause