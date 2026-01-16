@echo off
echo ========================================
echo   Iniciando Servidor HTML iGo Market
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando se Python esta instalado...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

echo.
echo Verificando se o arquivo HTML existe...
if not exist "frontend\public\igo_market_comparador_precos.html" (
    echo ERRO: Arquivo HTML nao encontrado!
    echo Caminho esperado: frontend\public\igo_market_comparador_precos.html
    pause
    exit /b 1
)

echo.
echo Iniciando servidor na porta 8000...
echo.
echo Servidor iniciado!
echo.
echo Acesse: http://localhost:8000/igo_market_comparador_precos.html
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python servidor_html.py

pause
