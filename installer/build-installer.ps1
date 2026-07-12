<#
    build-installer.ps1 — Compiles NicotineCafeSetup.iss into an installer
    .exe using Inno Setup's command-line compiler (ISCC.exe).

    Prerequisites:
      1. Run scripts\publish.ps1 first.
      2. Install Inno Setup: https://jrsoftware.org/isdl.php
#>

$ErrorActionPreference = "Stop"
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $iscc)) {
    throw "Inno Setup not found at '$iscc'. Install it from https://jrsoftware.org/isdl.php first."
}

$scriptPath = Join-Path $PSScriptRoot "NicotineCafeSetup.iss"
Write-Host "==> Compiling installer..." -ForegroundColor Cyan
& $iscc $scriptPath

if ($LASTEXITCODE -ne 0) { throw "ISCC compilation failed." }

Write-Host "==> Done. Installer is in installer\Output\NicotineCafeSetup.exe" -ForegroundColor Green
