#!/bin/bash

echo "========================================"
echo "  iGo Market - Comparador de Precos RJ"
echo "========================================"
echo ""
echo "Iniciando servidor backend..."
cd backend && python app.py &
BACKEND_PID=$!
sleep 3
echo ""
echo "Iniciando servidor frontend..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!
echo ""
echo "Servidores iniciados!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8000"
echo ""
echo "Pressione Ctrl+C para parar os servidores"
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait


