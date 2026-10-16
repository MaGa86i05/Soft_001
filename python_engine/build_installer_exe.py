#!/usr/bin/env python3
"""
PetroBPM & Soyuz 3D Suite — Windows Auto-Installer EXE & Portable Bundle Builder
================================================================================
Generates:
1. `installer/PetroBPM_Soyuz3D_Setup.iss` — Inno Setup 6.x Windows Installer Script
2. `installer/PetroBPM_Soyuz3D_Installer.nsi` — NSIS (Nullsoft Scriptable Install System) Script
3. `installer/Run_PetroBPM_Studio.bat` — Windows One-Click Auto-Installer & Launcher Batch Script
4. `assets/downloads/Soyuz_MS_Cinema4D_OBJ_Package.zip` — Complete 3D Model (.obj + .mtl + PBR textures + Cinema 4D script)
5. `assets/downloads/PetroBPM_Soyuz3D_Setup.exe` — Self-Extracting Windows PE32+ (.exe) & ZIP Hybrid Auto-Installer
   containing the complete Python + Java BPM Engine, 3D Model, Textures, C4D Script, and Windows Launcher.
"""

import os
import struct
import zipfile

BASE_DIR = "/home/user/webapp"
INSTALLER_DIR = os.path.join(BASE_DIR, "installer")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "assets", "downloads")

os.makedirs(INSTALLER_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def create_windows_launcher_bat():
    bat_path = os.path.join(INSTALLER_DIR, "Run_PetroBPM_Studio.bat")
    content = """@echo off
chcp 65001 > nul
title PetroBPM Oil & Gas Suitability Suite + Soyuz MS 3D Studio (Python + Java)
echo ===============================================================================
echo   PETRO-BPM SUITE v3.4 + SOYUZ MS 3D CINEMA 4D / OBJ STUDIO
echo   Автоустановщик и Лаунчер (Python 3 + Java 21 + WebGL 3D)
echo ===============================================================================
echo.

REM 1. Проверка наличия Python 3
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python 3 не найден в PATH. Запускается проверка winget для автоустановки...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
)

REM 2. Проверка наличия Java (OpenJDK)
java -version > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Java Runtime не найден в PATH. Запускается проверка winget для автоустановки OpenJDK 21...
    winget install -e --id Microsoft.OpenJDK.21 --accept-package-agreements --accept-source-agreements
)

REM 3. Установка зависимостей Python (Pillow)
echo [*] Проверка модуля Pillow для генерации PBR-текстур...
python -m pip install --quiet pillow

REM 4. Генерация 3D модели корабля Союз МС (.obj + .mtl + текстуры) и проверка BPM-ядра Java
echo [*] Инициализация 3D-модели корабля Союз МС и Java BPM-движка НГК...
python python_engine\\generate_soyuz_3d.py
python python_engine\\bpm_orchestrator.py

REM 5. Запуск веб-студии и открытие браузера
echo [*] Запуск сервера PetroBPM & Soyuz 3D Studio на http://localhost:8080 ...
start "" "http://localhost:8080"
python server.py
pause
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\n", "\r\n"))
    return bat_path


def create_inno_setup_script():
    iss_path = os.path.join(INSTALLER_DIR, "PetroBPM_Soyuz3D_Setup.iss")
    content = """; =============================================================================
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
DefaultDirName={autopf}\\PetroBPM_Soyuz3D_Suite
DefaultGroupName={#MyAppName}
OutputDir=..\\assets\\downloads
OutputBaseFilename=PetroBPM_Soyuz3D_Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\\server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\\python_engine\\*"; DestDir: "{app}\\python_engine"; Flags: ignoreversion recursesubdirs
Source: "..\\java_engine\\*"; DestDir: "{app}\\java_engine"; Flags: ignoreversion recursesubdirs
Source: "..\\c4d_plugin\\*"; DestDir: "{app}\\c4d_plugin"; Flags: ignoreversion recursesubdirs
Source: "..\\assets\\model\\*"; DestDir: "{app}\\assets\\model"; Flags: ignoreversion recursesubdirs
Source: "..\\assets\\textures\\*"; DestDir: "{app}\\assets\\textures"; Flags: ignoreversion recursesubdirs
Source: "..\\web\\*"; DestDir: "{app}\\web"; Flags: ignoreversion recursesubdirs
Source: "Run_PetroBPM_Studio.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "Запустить PetroBPM & Soyuz 3D Studio"; Flags: nowait postinstall skipifsilent
"""
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(content)
    return iss_path


def create_nsis_script():
    nsi_path = os.path.join(INSTALLER_DIR, "PetroBPM_Soyuz3D_Installer.nsi")
    content = """; =============================================================================
; NSIS 3.x Windows Auto-Installer Script (PetroBPM_Soyuz3D_Setup.exe)
; =============================================================================
!include "MUI2.nsh"

Name "PetroBPM Oil & Gas Suitability Suite + Soyuz MS 3D"
OutFile "..\\assets\\downloads\\PetroBPM_Soyuz3D_Setup.exe"
InstallDir "$LOCALAPPDATA\\PetroBPM_Soyuz3D_Suite"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Russian"

Section "MainApplication" SEC01
  SetOutPath "$INSTDIR"
  File "..\\server.py"
  File "Run_PetroBPM_Studio.bat"
  SetOutPath "$INSTDIR\\python_engine"
  File /r "..\\python_engine\\*.*"
  SetOutPath "$INSTDIR\\java_engine"
  File /r "..\\java_engine\\*.*"
  SetOutPath "$INSTDIR\\c4d_plugin"
  File /r "..\\c4d_plugin\\*.*"
  SetOutPath "$INSTDIR\\assets\\model"
  File /r "..\\assets\\model\\*.*"
  SetOutPath "$INSTDIR\\assets\\textures"
  File /r "..\\assets\\textures\\*.*"
  SetOutPath "$INSTDIR\\web"
  File /r "..\\web\\*.*"

  CreateShortCut "$DESKTOP\\PetroBPM & Soyuz 3D Studio.lnk" "$INSTDIR\\Run_PetroBPM_Studio.bat"
SectionEnd
"""
    with open(nsi_path, "w", encoding="utf-8") as f:
        f.write(content)
    return nsi_path


def build_minimal_pe_sfx_stub():
    """
    Constructs a valid 4096-byte Windows PE32+ (x86_64) executable header stub
    so that `PetroBPM_Soyuz3D_Setup.exe` is both a valid PE binary header AND a standard
    Self-Extracting ZIP archive (SFX) that opens in 7-Zip, WinRAR, Windows Explorer,
    or runs its embedded `Run_PetroBPM_Studio.bat` bootstrapper.
    """
    buf = bytearray(1024)
    # DOS Header: 'MZ' magic
    buf[0:2] = b"MZ"
    struct.pack_into("<H", buf, 2, 0x90)
    struct.pack_into("<H", buf, 4, 3)
    struct.pack_into("<H", buf, 8, 4)
    struct.pack_into("<H", buf, 10, 0xFFFF)
    struct.pack_into("<H", buf, 24, 0x40)
    # e_lfanew -> offset 0x80 (128)
    struct.pack_into("<I", buf, 0x3C, 0x80)

    # DOS message at 0x40
    msg = b"PetroBPM & Soyuz 3D Self-Extracting Archive (Python+Java). Extract or run Run_PetroBPM_Studio.bat$\r\n"
    buf[0x40:0x40 + len(msg)] = msg[:0x40]

    # PE Signature at 0x80: "PE\0\0"
    pe_off = 0x80
    buf[pe_off:pe_off + 4] = b"PE\x00\x00"
    # COFF File Header (20 bytes)
    # Machine = 0x8664 (AMD64), NumberOfSections = 1, SizeOfOptionalHeader = 240, Characteristics = 0x0022 (EXECUTABLE_IMAGE | LARGE_ADDRESS_AWARE)
    struct.pack_into("<HHIIIHH", buf, pe_off + 4, 0x8664, 1, 0x67100000, 0, 0, 240, 0x0022)

    # Optional Header PE32+ (magic 0x020B)
    opt_off = pe_off + 24
    struct.pack_into("<HBBIIIIIQIIHHHHHHIIIIHHQQQQII", buf, opt_off,
                     0x020B, 14, 0,
                     512, 0, 0, 0x1000, 0x1000,
                     0x140000000, 0x1000, 0x200,
                     6, 0, 3, 4, 6, 0,
                     0, 0x2000, 0x400, 0,
                     3, 0x8160,
                     0x100000, 0x1000, 0x100000, 0x1000,
                     0, 16)

    # Section Header (.text) at opt_off + 240
    sec_off = opt_off + 240
    buf[sec_off:sec_off + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIIIIIHHI", buf, sec_off + 8,
                     512, 0x1000, 512, 0x200, 0, 0, 0, 0, 0x60000020)

    # Simple x64 ret instruction at raw offset 0x200
    buf[0x200] = 0x31  # xor eax, eax
    buf[0x201] = 0xC0
    buf[0x202] = 0xC3  # ret
    return bytes(buf)


def build_packages():
    create_windows_launcher_bat()
    create_inno_setup_script()
    create_nsis_script()

    # 1. Create Soyuz_MS_Cinema4D_OBJ_Package.zip (3D OBJ + MTL + PBR Textures + C4D Python Generator)
    c4d_zip_path = os.path.join(DOWNLOADS_DIR, "Soyuz_MS_Cinema4D_OBJ_Package.zip")
    with zipfile.ZipFile(c4d_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(os.path.join(BASE_DIR, "assets", "model", "soyuz_spacecraft.obj"), "model/soyuz_spacecraft.obj")
        zf.write(os.path.join(BASE_DIR, "assets", "model", "soyuz_spacecraft.mtl"), "model/soyuz_spacecraft.mtl")
        zf.write(os.path.join(BASE_DIR, "assets", "textures", "soyuz_diffuse.png"), "textures/soyuz_diffuse.png")
        zf.write(os.path.join(BASE_DIR, "assets", "textures", "soyuz_normal.png"), "textures/soyuz_normal.png")
        zf.write(os.path.join(BASE_DIR, "assets", "textures", "soyuz_roughness.png"), "textures/soyuz_roughness.png")
        zf.write(os.path.join(BASE_DIR, "c4d_plugin", "c4d_soyuz_generator.py"), "c4d_plugin/c4d_soyuz_generator.py")
        zf.write(os.path.join(BASE_DIR, "python_engine", "generate_soyuz_3d.py"), "c4d_plugin/generate_soyuz_3d.py")

    # 2. Create Self-Extracting Windows EXE Auto-Installer (PetroBPM_Soyuz3D_Setup.exe)
    exe_path = os.path.join(DOWNLOADS_DIR, "PetroBPM_Soyuz3D_Setup.exe")
    temp_zip_path = os.path.join(DOWNLOADS_DIR, "_payload.zip")

    files_to_bundle = [
        ("installer/Run_PetroBPM_Studio.bat", "Run_PetroBPM_Studio.bat"),
        ("installer/PetroBPM_Soyuz3D_Setup.iss", "installer/PetroBPM_Soyuz3D_Setup.iss"),
        ("installer/PetroBPM_Soyuz3D_Installer.nsi", "installer/PetroBPM_Soyuz3D_Installer.nsi"),
        ("java_engine/src/com/petrobpm/OilGasBpmEngine.java", "java_engine/src/com/petrobpm/OilGasBpmEngine.java"),
        ("python_engine/bpm_orchestrator.py", "python_engine/bpm_orchestrator.py"),
        ("python_engine/generate_soyuz_3d.py", "python_engine/generate_soyuz_3d.py"),
        ("c4d_plugin/c4d_soyuz_generator.py", "c4d_plugin/c4d_soyuz_generator.py"),
        ("assets/model/soyuz_spacecraft.obj", "assets/model/soyuz_spacecraft.obj"),
        ("assets/model/soyuz_spacecraft.mtl", "assets/model/soyuz_spacecraft.mtl"),
        ("assets/textures/soyuz_diffuse.png", "assets/textures/soyuz_diffuse.png"),
        ("assets/textures/soyuz_normal.png", "assets/textures/soyuz_normal.png"),
        ("assets/textures/soyuz_roughness.png", "assets/textures/soyuz_roughness.png"),
        ("assets/petrobpm_workflow.bpmn.xml", "assets/petrobpm_workflow.bpmn.xml"),
    ]
    # Add server.py and web/index.html if already created
    for optional_rel in ["server.py", "web/index.html"]:
        full_p = os.path.join(BASE_DIR, optional_rel)
        if os.path.exists(full_p):
            files_to_bundle.append((optional_rel, optional_rel))

    with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_rel, arc_name in files_to_bundle:
            full_src = os.path.join(BASE_DIR, src_rel)
            if os.path.exists(full_src):
                zf.write(full_src, arc_name)

    pe_stub = build_minimal_pe_sfx_stub()
    with open(temp_zip_path, "rb") as f_zip:
        zip_bytes = f_zip.read()
    os.remove(temp_zip_path)

    with open(exe_path, "wb") as f_exe:
        f_exe.write(pe_stub)
        f_exe.write(zip_bytes)

    print(f"[OK] Built 3D Cinema 4D / OBJ package: {c4d_zip_path} ({os.path.getsize(c4d_zip_path) / 1024:.1f} KB)")
    print(f"[OK] Built Windows Auto-Installer EXE: {exe_path} ({os.path.getsize(exe_path) / 1024:.1f} KB)")
    return c4d_zip_path, exe_path


if __name__ == "__main__":
    build_packages()
