@echo off
cd /d "%~dp0"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
pause
