@echo off
setlocal
cd /d "%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0runtime\launcher.ps1"
if errorlevel 1 (
  echo.
  echo CampusBot did not start correctly. Review the message above.
  pause
)
endlocal
