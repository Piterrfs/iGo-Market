@echo off
echo ========================================
echo   Diagnostico dos Servidores iGo Market
echo ========================================
echo.

echo Verificando servidor HTML (porta 8000)...
netstat -ano | findstr :8000 | findstr LISTENING >nul
if errorlevel 1 (
    echo [X] Servidor HTML nao esta rodando na porta 8000
) else (
    echo [OK] Servidor HTML esta rodando na porta 8000
    netstat -ano | findstr :8000 | findstr LISTENING
)

echo.
echo Verificando servidor Backend (porta 5000)...
netstat -ano | findstr :5000 | findstr LISTENING >nul
if errorlevel 1 (
    echo [X] Servidor Backend nao esta rodando na porta 5000
) else (
    echo [OK] Servidor Backend esta rodando na porta 5000
    netstat -ano | findstr :5000 | findstr LISTENING
)

echo.
echo Verificando arquivos...
if exist "frontend\public\igo_market_comparador_precos.html" (
    echo [OK] Arquivo HTML encontrado
) else (
    echo [X] Arquivo HTML NAO encontrado
)

if exist "backend\app.py" (
    echo [OK] Arquivo app.py encontrado
) else (
    echo [X] Arquivo app.py NAO encontrado
)

echo.
echo ========================================
echo   Testando importacao do backend...
echo ========================================
cd backend
python -c "import sys; sys.path.insert(0, '.'); from app import app; print('[OK] Backend pode ser importado')" 2>&1
cd ..

echo.
echo ========================================
pause
