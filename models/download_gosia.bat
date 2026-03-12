@echo off
setlocal

for %%I in ("%~dp0.") do set "SCRIPT_DIR=%%~fI"
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\download_gosia.ps1" -OutDir "%SCRIPT_DIR%"

if errorlevel 1 (
  echo Download failed.
  pause
  exit /b 1
)

echo Download completed successfully.
pause
