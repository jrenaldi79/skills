# Windows Onboarding - Dependency Installation Script
# Installs Chocolatey, Python (Embeddable Strategy), and Git

$ErrorActionPreference = "Continue"

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
}

function Remove-PythonCompletely {
    try {
        Write-Host "Performing complete Python cleanup..." -ForegroundColor Cyan
        
        # Uninstall all Chocolatey Python packages
        choco uninstall python python3 python312 python313 python314 -y --force 2>&1 | Out-Null
        
        # Remove installation directories
        $pythonDirs = @(
            "C:\Python312",
            "C:\Python313", 
            "C:\Python314",
            "C:\Program Files\Python312",
            "C:\Program Files\Python313",
            "C:\Program Files\Python314"
        )
        
        foreach ($dir in $pythonDirs) {
            if (Test-Path $dir) {
                Write-Host "  Removing $dir..." -ForegroundColor Yellow
                Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        
        # Clean PATH with error handling
        try {
            $currentPath = [System.Environment]::GetEnvironmentVariable('Path','Machine')
            
            if ([string]::IsNullOrWhiteSpace($currentPath)) {
                Write-Host "[WARNING] PATH is empty, skipping cleanup" -ForegroundColor Yellow
            } else {
                $pathParts = ($currentPath -split ";") | Where-Object { 
                    $_ -notlike "*Python*" 
                }
                $cleanedPath = $pathParts -join ";"
                [System.Environment]::SetEnvironmentVariable('Path', $cleanedPath, 'Machine')
            }
        } catch {
            Write-Host "[WARNING] Could not clean PATH automatically: $_" -ForegroundColor Yellow
            Write-Host "Python may still work. Continuing..." -ForegroundColor Yellow
        }
        
        Refresh-Path
        Write-Host "[OK] Python cleanup complete" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Cleanup encountered issues but continuing: $_" -ForegroundColor Yellow
    }
}

function Test-PythonInstallation {
    param([string]$PythonPath)
    
    # Level 1: File exists
    $exePath = "$PythonPath\python.exe"
    if (-not (Test-Path $exePath)) {
        Write-Host "[FAIL] Python executable not found at $exePath" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] Python executable found" -ForegroundColor Green
    
    # Level 2: Executable runs
    try {
        $version = & $exePath --version 2>&1
        if ($version -notmatch "Python \d+\.\d+\.\d+") {
            Write-Host "[FAIL] Version check returned unexpected output: $version" -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] Python version check successful: $version" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Python executable failed to run: $_" -ForegroundColor Red
        return $false
    }
    
    # Level 3: Standard library present (Embeddable zip usually has python312.zip, not Lib folder directly, but we check for import capability)
    # Level 4: Can import and run simple script
    $testScript = "import sys; import os; print('OK')"
    try {
        $result = & $exePath -c $testScript 2>&1
        if ($result -ne "OK") {
            Write-Host "[FAIL] Script execution test failed: $result" -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] Python can execute scripts and import standard modules" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Script execution failed: $_" -ForegroundColor Red
        return $false
    }
    
    Write-Host "[SUCCESS] Python installation fully validated" -ForegroundColor Green
    return $true
}

function Install-PythonEmbeddable {
    $version = "3.12.0"
    $zipUrl = "https://www.python.org/ftp/python/$version/python-$version-embed-amd64.zip"
    $pythonPath = "C:\Python312"
    
    Write-Host "Downloading Python embeddable package ($version)..." -ForegroundColor Cyan
    $zipPath = "$env:TEMP\python-embed.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    
    Write-Host "Extracting to $pythonPath..." -ForegroundColor Cyan
    if (Test-Path $pythonPath) { Remove-Item $pythonPath -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $pythonPath | Out-Null
    Expand-Archive -Path $zipPath -DestinationPath $pythonPath -Force
    Remove-Item $zipPath
    
    # Enable pip support by uncommenting 'import site' in ._pth file
    $pthFile = "$pythonPath\python312._pth"
    if (Test-Path $pthFile) {
        $content = Get-Content $pthFile
        $content = $content -replace '#import site', 'import site'
        $content | Set-Content $pthFile
    }
    
    # Download and install pip
    Write-Host "Downloading get-pip.py..." -ForegroundColor Cyan
    $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
    $getPipPath = "$pythonPath\get-pip.py"
    Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath
    
    Write-Host "Installing pip..." -ForegroundColor Cyan
    & "$pythonPath\python.exe" "$getPipPath" | Out-Null
    Remove-Item "$getPipPath"
    
    # Add to PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable('Path','Machine')
    if ($currentPath -notlike "*$pythonPath*") {
        Write-Host "Adding Python to System PATH..." -ForegroundColor Cyan
        $newPath = $currentPath + ";$pythonPath;$pythonPath\Scripts"
        [System.Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')
    }
    
    Refresh-Path
    return $pythonPath
}

function Show-PythonDiagnostics {
    Write-Host "`n=== PYTHON INSTALLATION DIAGNOSTICS ===" -ForegroundColor Yellow
    Write-Host "PATH: $env:Path" -ForegroundColor DarkGray
    Write-Host "Searching for python.exe..." -ForegroundColor Cyan
    Get-ChildItem -Path "C:\" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue -Depth 3 | ForEach-Object { Write-Host "  Found: $($_.FullName)" -ForegroundColor Yellow }
}

# --- MAIN INSTALLATION LOGIC ---

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
        if ($null -eq (Get-Command choco -ErrorAction SilentlyContinue)) { throw "Chocolatey installed but not found in PATH" }
        Write-Host "[OK] Chocolatey installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install Chocolatey: $_" -ForegroundColor Red
        exit 1
    }
}

Refresh-Path
Write-Host ""

# 2. Python (Embeddable Strategy)
Write-Host "Checking for Python..." -ForegroundColor Cyan

# Check if already installed and working
$existingPython = Get-Command python -ErrorAction SilentlyContinue
$pythonWorking = $false
if ($existingPython) {
    if (Test-PythonInstallation -PythonPath ($existingPython.Source | Split-Path)) {
        $pythonWorking = $true
        Write-Host "[OK] Python is already installed and working" -ForegroundColor Green
    }
}

if (-not $pythonWorking) {
    # Clean up any broken installs first
    Remove-PythonCompletely
    
    Write-Host "Installing Python (Embeddable Strategy)..." -ForegroundColor Yellow
    try {
        $pythonPath = Install-PythonEmbeddable
        
        if (Test-PythonInstallation -PythonPath $pythonPath) {
            Write-Host "[OK] Python installed successfully via embeddable package" -ForegroundColor Green
        } else {
            throw "Python installation failed verification"
        }
    } catch {
        Write-Host "[FAIL] Python installation failed: $_" -ForegroundColor Red
        Show-PythonDiagnostics
        exit 1
    }
}

Write-Host ""

# 3. Git
Write-Host "Checking for Git..." -ForegroundColor Cyan
if ($null -ne (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[OK] Git is already installed" -ForegroundColor Green
} else {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    try {
        choco install git -y --force
        Refresh-Path
        if ($null -ne (Get-Command git -ErrorAction SilentlyContinue)) {
            $v = git --version 2>&1
            Write-Host "[OK] Git installed successfully: $v" -ForegroundColor Green
        } else {
            throw "Git installed but failed verification"
        }
    } catch {
        Write-Host "ERROR: Failed to install Git: $_" -ForegroundColor Red
    }
}

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