@echo off
cd /d "%~dp0"
call setup_windows.bat
if errorlevel 1 exit /b 1
call start_windows.bat
