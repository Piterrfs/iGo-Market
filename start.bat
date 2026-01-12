@echo off
echo ========================================
echo   iGo Market - Comparador de Precos RJ
echo ========================================
echo.
echo Iniciando servidor backend...
start cmd /k "cd backend && python app.py"
timeout /t 3
echo.
echo Iniciando servidor frontend...
start cmd /k "cd frontend && npm run dev"
echo.
echo Servidores iniciados!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8000
echo.
pause


