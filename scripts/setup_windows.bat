@echo off
REM Usage: setup_windows.bat [cuda]
SETLOCAL ENABLEDELAYEDEXPANSION

where py >nul 2>nul
IF ERRORLEVEL 1 (
  echo Python Launcher not found. Install Python 3 and ensure 'py' is in PATH.
  exit /b 1
)

IF "%1"=="cuda" (
  powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1 -Cuda
) ELSE (
  powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
)
ENDLOCAL
