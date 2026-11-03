@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto launch
call setup_windows.bat
if errorlevel 1 exit /b 1
:launch
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto fail
echo Open http://127.0.0.1:8000/ in your browser.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
:fail
pause
