<#
    publish.ps1 — Builds a self-contained, ready-to-install copy of the
    WPF app (no .NET runtime needed on the target machine) plus the
    voice-engine and database, into .\publish\NicotineCafe.

    Run this from the repo root (where NicotineCafe.sln lives), on a
    machine with the .NET 8 SDK installed:

        powershell -ExecutionPolicy Bypass -File scripts\publish.ps1
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$publishDir = Join-Path $root "publish\NicotineCafe"

Write-Host "==> Cleaning previous publish output..." -ForegroundColor Cyan
if (Test-Path $publishDir) { Remove-Item $publishDir -Recurse -Force }
New-Item -ItemType Directory -Path $publishDir | Out-Null

Write-Host "==> Publishing NicotineCafe.WPF (self-contained, win-x64)..." -ForegroundColor Cyan
dotnet publish "$root\src\NicotineCafe.WPF\NicotineCafe.WPF.csproj" `
    -c Release `
    -r win-x64 `
    --self-contained true `
    -p:PublishSingleFile=false `
    -p:IncludeNativeLibrariesForSelfExtract=true `
    -o $publishDir

if ($LASTEXITCODE -ne 0) { throw "dotnet publish failed." }

Write-Host "==> Verifying voice-engine and database were copied..." -ForegroundColor Cyan
$mustExist = @(
    (Join-Path $publishDir "voice-engine\main.py"),
    (Join-Path $publishDir "Data\nicotinecafe.db")
)
foreach ($p in $mustExist) {
    if (-not (Test-Path $p)) {
        Write-Warning "Missing expected file: $p — check the csproj CopyToOutputDirectory items."
    }
}

Write-Host ""
Write-Host "==> Done. Publish output is in: $publishDir" -ForegroundColor Green
Write-Host "    Next: run installer\build-installer.ps1 (needs Inno Setup) to create the .exe installer." -ForegroundColor Green
