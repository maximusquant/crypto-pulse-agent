@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
echo Запуск main.py...
.venv\Scripts\python.exe -u main.py
echo.
echo Код выхода: %ERRORLEVEL%
pause
