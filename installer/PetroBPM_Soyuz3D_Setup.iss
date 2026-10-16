; =============================================================================
; Inno Setup 6.x Auto-Installer Script for Windows 10 / 11 (x64)
; Программа создания и тестирования на пригодность БП нефтегазового производства
; (Python + Java) + 3D Модель Космического корабля «Союз МС» (Cinema 4D / OBJ)
; =============================================================================

#define MyAppName "PetroBPM Oil & Gas Suitability Suite + Soyuz MS 3D"
#define MyAppVersion "3.4.0"
#define MyAppPublisher "PetroBPM & Aerospace CAD Engineering"
#define MyAppExeName "Run_PetroBPM_Studio.bat"

[Setup]
AppId={{B8F41C2A-94E2-4D18-9A55-7E210C4F8891}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\PetroBPM_Soyuz3D_Suite
DefaultGroupName={#MyAppName}
OutputDir=..\assets\downloads
OutputBaseFilename=PetroBPM_Soyuz3D_Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\python_engine\*"; DestDir: "{app}\python_engine"; Flags: ignoreversion recursesubdirs
Source: "..\java_engine\*"; DestDir: "{app}\java_engine"; Flags: ignoreversion recursesubdirs
Source: "..\c4d_plugin\*"; DestDir: "{app}\c4d_plugin"; Flags: ignoreversion recursesubdirs
Source: "..\assets\model\*"; DestDir: "{app}\assets\model"; Flags: ignoreversion recursesubdirs
Source: "..\assets\textures\*"; DestDir: "{app}\assets\textures"; Flags: ignoreversion recursesubdirs
Source: "..\web\*"; DestDir: "{app}\web"; Flags: ignoreversion recursesubdirs
Source: "Run_PetroBPM_Studio.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить PetroBPM & Soyuz 3D Studio"; Flags: nowait postinstall skipifsilent
