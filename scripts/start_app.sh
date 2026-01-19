#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🚀 Iniciando Backend e Banco de Dados..."
docker-compose up -d --build
echo "✅ Sistema online! API disponível em http://localhost:8001"
