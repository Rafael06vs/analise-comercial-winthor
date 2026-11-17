@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =======================================
echo      ANALISE COMERCIAL - RELATORIOS
echo =======================================
echo.
where python >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado. Instale o Python e tente novamente.
    pause
    exit /b 1
)
python scripts\analisar.py
if errorlevel 1 (
    echo.
    echo Falha ao gerar relatorios. Veja o erro acima.
    pause
    exit /b 1
)
echo.
echo Abrindo pasta de relatorios...
start "" "%~dp0relatorios"
echo CSVs: dados\saida
pause
