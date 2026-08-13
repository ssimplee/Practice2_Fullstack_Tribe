@echo off
setlocal
cd /d "%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0runtime\run_tests.ps1"
if errorlevel 1 (
  echo.
  echo One or more tests failed. Review the output above.
)
pause
endlocal
