@echo off
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
python python_engine\generate_soyuz_3d.py
python python_engine\bpm_orchestrator.py

REM 5. Запуск веб-студии и открытие браузера
echo [*] Запуск сервера PetroBPM & Soyuz 3D Studio на http://localhost:8080 ...
start "" "http://localhost:8080"
python server.py
pause
