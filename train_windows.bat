@echo off
cd /d %~dp0
if not exist .venv (
    echo Environnement Python introuvable.
    echo Lancez d'abord les commandes d'installation du README.
    pause
    exit /b 1
)
call .venv\Scripts\activate
python src\train_model.py
pause
