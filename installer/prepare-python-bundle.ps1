<#
    prepare-python-bundle.ps1 — Run ONCE, on a machine WITH internet, to
    build two folders at the solution root:

        python-embed\   — a private, portable Python (no system install,
                           no PATH changes) with every voice-engine pip
                           package already installed inside it
        model-cache\     — a pre-downloaded faster-whisper model, so the
                           app never needs to hit Hugging Face at all

    Both folders are picked up automatically by the WPF csproj and copied
    into publish\NicotineCafe\ the next time you run scripts\publish.ps1 —
    the final installer.exe built from that is then 100% offline: no
    system Python, no internet, nothing to install by hand on the shop PC.

    Usage:
        powershell -ExecutionPolicy Bypass -File installer\prepare-python-bundle.ps1
        powershell -ExecutionPolicy Bypass -File installer\prepare-python-bundle.ps1 -ModelSize small
#>

param(
    [string]$PythonVersion = "3.11.9",
    [ValidateSet("tiny", "base", "small")]
    [string]$ModelSize = "tiny"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$pythonDir = Join-Path $root "python-embed"
$modelCacheDir = Join-Path $root "model-cache"
$voiceEngineDir = Join-Path $root "voice-engine"

# ---------------------------------------------------------------------
# 1) Download the embeddable Python distribution (no installer, no PATH
#    changes, no admin rights — just a folder of files).
# ---------------------------------------------------------------------
Write-Host "==> [1/6] Downloading Python $PythonVersion (embeddable, amd64)..." -ForegroundColor Cyan
if (Test-Path $pythonDir) { Remove-Item $pythonDir -Recurse -Force }
New-Item -ItemType Directory -Path $pythonDir | Out-Null

$embedUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
$embedZip = Join-Path $env:TEMP "python-embed.zip"
Invoke-WebRequest -Uri $embedUrl -OutFile $embedZip
Expand-Archive -Path $embedZip -DestinationPath $pythonDir -Force
Remove-Item $embedZip

# ---------------------------------------------------------------------
# 2) Enable site-packages in the embeddable distro (disabled by default).
#    The ._pth file has a commented-out "#import site" line — uncomment it.
# ---------------------------------------------------------------------
Write-Host "==> [2/6] Enabling site-packages..." -ForegroundColor Cyan
$pthFile = Get-ChildItem $pythonDir -Filter "python*._pth" | Select-Object -First 1
(Get-Content $pthFile.FullName) -replace '#\s*import site', 'import site' | Set-Content $pthFile.FullName

# ---------------------------------------------------------------------
# 3) Bootstrap pip inside the embeddable distro.
# ---------------------------------------------------------------------
Write-Host "==> [3/6] Installing pip..." -ForegroundColor Cyan
$getPipPath = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipPath
& "$pythonDir\python.exe" $getPipPath --no-warn-script-location
Remove-Item $getPipPath

# ---------------------------------------------------------------------
# 4) Install every voice-engine dependency INTO this private Python.
# ---------------------------------------------------------------------
Write-Host "==> [4/6] Installing voice-engine requirements..." -ForegroundColor Cyan
& "$pythonDir\python.exe" -m pip install -r "$voiceEngineDir\requirements.txt" --no-warn-script-location

if ($LASTEXITCODE -ne 0) { throw "pip install failed — check the error above." }

# ---------------------------------------------------------------------
# 5) Pre-download the Whisper model into model-cache\ (so the shop PC
#    never needs internet, not even on first run).
# ---------------------------------------------------------------------
Write-Host "==> [5/6] Pre-downloading the '$ModelSize' Whisper model..." -ForegroundColor Cyan
if (Test-Path $modelCacheDir) { Remove-Item $modelCacheDir -Recurse -Force }
New-Item -ItemType Directory -Path $modelCacheDir | Out-Null

$env:HF_HOME = $modelCacheDir
& "$pythonDir\python.exe" -c "from faster_whisper import WhisperModel; WhisperModel('$ModelSize', device='cpu', compute_type='int8'); print('Model cached.')"

if ($LASTEXITCODE -ne 0) { throw "Model pre-download failed — check the error above." }

# ---------------------------------------------------------------------
# 6) Sanity check.
# ---------------------------------------------------------------------
Write-Host "==> [6/6] Verifying the bundle..." -ForegroundColor Cyan
$checks = @(
    (Join-Path $pythonDir "python.exe"),
    (Join-Path $modelCacheDir "hub")
)
$ok = $true
foreach ($c in $checks) {
    if (-not (Test-Path $c)) { Write-Warning "Missing: $c"; $ok = $false }
}

Write-Host ""
if ($ok) {
    Write-Host "==> Done. python-embed\ and model-cache\ are ready at the solution root." -ForegroundColor Green
    Write-Host "    Next: run scripts\publish.ps1, then installer\build-installer.ps1." -ForegroundColor Green
} else {
    Write-Warning "Something looks off — check the warnings above before publishing."
}
