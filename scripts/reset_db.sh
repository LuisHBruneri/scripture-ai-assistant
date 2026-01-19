#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🗑️  Resetando o Banco de Dados (ChromaDB)..."

# 1. Stop containers and remove volumes
docker-compose down -v

echo "🧹 Volume de dados removido."

# 2. Restart containers
echo "🔄 Reiniciando containers..."
docker-compose up -d

echo "✨ Banco de dados limpo e containers rodando!"
echo "⚠️  Nota: O banco está vazio. Execute 'scripts/refresh_knowledge.sh' para re-ingerir os documentos."
