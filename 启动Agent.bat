@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus AI Agent
echo ============================================================
echo.
echo   [INFO] Starting OpenManus Agent...
echo.

REM --- Detect OpenManus installation directory ---
set "OPENMANUS_DIR=%~dp0"
if exist "%OPENMANUS_DIR%main.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
set "OPENMANUS_DIR=%USERPROFILE%\OpenManus"
if exist "%OPENMANUS_DIR%\main.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
set "OPENMANUS_DIR=E:\OpenManus"
if exist "%OPENMANUS_DIR%\main.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
echo [ERROR] Cannot find OpenManus directory!
echo Please place this file in your OpenManus folder.
pause
exit /b 1

:found
echo   Directory: %CD%
echo.

REM --- Activate virtual environment ---
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    echo Please run the install script first.
    pause
    exit /b 1
)

REM --- Show current model ---
echo   Current config:
findstr /B "model" config\config.toml 2>nul | findstr /V "#"
echo.
echo ============================================================
echo.

python main.py
pause
