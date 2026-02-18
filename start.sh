#!/bin/bash

echo "🚀 Iniciando MarketRadar..."
echo ""
echo "1. Iniciando API backend na porta 8000..."
cd backend
python api.py &
API_PID=$!
cd ..

echo "2. Aguardando API iniciar..."
sleep 3

echo "3. Para iniciar o frontend, execute em outro terminal:"
echo "   cd frontend"
echo "   npm install"
echo "   npm start"
echo ""
echo "API rodando em http://localhost:8000"
echo "Frontend estará disponível em http://localhost:3000"
echo ""
echo "Pressione Ctrl+C para parar a API"

wait $API_PID
