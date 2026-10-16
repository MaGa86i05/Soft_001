; =============================================================================
; NSIS 3.x Windows Auto-Installer Script (PetroBPM_Soyuz3D_Setup.exe)
; =============================================================================
!include "MUI2.nsh"

Name "PetroBPM Oil & Gas Suitability Suite + Soyuz MS 3D"
OutFile "..\assets\downloads\PetroBPM_Soyuz3D_Setup.exe"
InstallDir "$LOCALAPPDATA\PetroBPM_Soyuz3D_Suite"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "Russian"

Section "MainApplication" SEC01
  SetOutPath "$INSTDIR"
  File "..\server.py"
  File "Run_PetroBPM_Studio.bat"
  SetOutPath "$INSTDIR\python_engine"
  File /r "..\python_engine\*.*"
  SetOutPath "$INSTDIR\java_engine"
  File /r "..\java_engine\*.*"
  SetOutPath "$INSTDIR\c4d_plugin"
  File /r "..\c4d_plugin\*.*"
  SetOutPath "$INSTDIR\assets\model"
  File /r "..\assets\model\*.*"
  SetOutPath "$INSTDIR\assets\textures"
  File /r "..\assets\textures\*.*"
  SetOutPath "$INSTDIR\web"
  File /r "..\web\*.*"

  CreateShortCut "$DESKTOP\PetroBPM & Soyuz 3D Studio.lnk" "$INSTDIR\Run_PetroBPM_Studio.bat"
SectionEnd
