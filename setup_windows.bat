@echo off
cd /d %~dp0
echo =============================================
echo Installation du prototype ONDA Risk
echo =============================================
python --version
if errorlevel 1 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Installez Python 3.12 ou 3.13 puis relancez ce fichier.
    pause
    exit /b 1
)
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\train_model.py
echo.
echo Installation terminee.
echo Lancez ensuite run_windows.bat
pause
