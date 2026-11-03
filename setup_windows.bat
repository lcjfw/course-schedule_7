@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto install
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m venv .venv
if errorlevel 1 goto fail
goto install
:usepython
python -m venv .venv
if errorlevel 1 goto fail
:install
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto fail
exit /b 0
:fail
echo Setup failed. Install Python 3.10 or later and check your network.
pause
exit /b 1
