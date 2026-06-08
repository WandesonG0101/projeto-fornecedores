@echo off
cd /d "%~dp0"
echo Iniciando o servidor Django em http://127.0.0.1:8000/login/
echo.
python manage.py runserver 127.0.0.1:8000 --noreload
pause
