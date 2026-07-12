; ==========================================================================
; NicotineCafeSetup.iss — Inno Setup script
;
; Builds a single, fully OFFLINE installer .exe that:
;   1. Copies the published WPF app (self-contained — no .NET needed)
;   2. Copies the voice-engine (Python) folder + shared SQLite database
;   3. Copies a bundled, private Python (python-embed\) with every pip
;      package already installed — no system Python, no internet, ever
;   4. Copies a pre-downloaded Whisper model cache (model-cache\) — no
;      Hugging Face download needed on first run either
;   5. Creates Desktop + Start Menu shortcuts
;
; HOW TO BUILD:
;   1. Run installer\prepare-python-bundle.ps1 ONCE on a machine with
;      internet (see README) — produces python-embed\ and model-cache\
;      at the solution root.
;   2. Run scripts\publish.ps1 (picks up python-embed\ and model-cache\
;      automatically via the csproj).
;   3. Install Inno Setup: https://jrsoftware.org/isdl.php
;   4. Run installer\build-installer.ps1 (or open this file and Compile).
;   5. Output installer .exe appears in installer\Output\
; ==========================================================================

#define MyAppName "Nicotine Cafe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nicotine Cafe"
#define MyAppExeName "NicotineCafe.exe"
#define PublishDir "..\publish\NicotineCafe"

[Setup]
AppId={{B3E1B2B0-4C1E-4E6B-9B7E-NICOTINECAFE1}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\NicotineCafe
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=NicotineCafeSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Everything from the published output (exe, dlls, voice-engine\, Data\, Assets\, ...)
Source: "{#PublishDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای Nicotine Cafe"; Flags: postinstall nowait skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Nothing to check here anymore — Python + all pip packages are bundled
  // in python-embed\ (see installer\prepare-python-bundle.ps1), so this
  // installer needs neither a system Python install nor internet access.
  if not FileExists(ExpandConstant('{src}\..\publish\NicotineCafe\python-embed\python.exe')) then
  begin
    MsgBox('پوشه‌ی python-embed توی publish\NicotineCafe پیدا نشد.' + #13#10 +
           'اول اسکریپت installer\prepare-python-bundle.ps1 رو اجرا کن، بعد دوباره publish.ps1 رو بزن، ' +
           'بعد این installer رو دوباره بساز.',
           mbError, MB_OK);
    Result := False;
  end;
end;
