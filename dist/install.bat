@echo off
chcp 65001 >nul
color 0A
title Arrow Detector - Instalador

echo.
echo ╔════════════════════════════════════════════╗
echo ║   Arrow Detector - Setup de Instalação    ║
echo ╚════════════════════════════════════════════╝
echo.


echo.
echo 📥 Instalando dependências...
pip install --upgrade pip -q
pip install -r requirements.txt -q

if errorlevel 1 (
    echo ✗ Erro ao instalar dependências
    echo Tente executar manualmente:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Dependências instaladas com sucesso!

REM Executar a aplicação
echo.
echo ✓ Iniciando Arrow Detector...
echo.

start "" lockpick.exe

exit /b 0