@echo off
cd /d "%~dp0"
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias do dashboard...
  python -m pip install -r requirements-dashboard.txt
  if errorlevel 1 (
    echo.
    echo Falha ao instalar. Confira a versao do Python e a conexao com a internet.
    pause
    exit /b 1
  )
)
python -m streamlit run dashboard.py
if errorlevel 1 pause
