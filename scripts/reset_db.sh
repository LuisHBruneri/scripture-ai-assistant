#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🗑️  Resetando o Banco de Dados (ChromaDB)..."

# 1. Stop containers
docker-compose down

# 2. Force delete local data folder
echo "🔥 Removendo arquivos locais de ./data/chroma_db ..."
rm -rf data/chroma_db

echo "🧹 Dados removidos."

# 3. Restart containers
echo "🔄 Reiniciando containers..."
docker-compose up -d

echo "✨ Banco de dados limpo e containers rodando!"
echo "⚠️  Nota: O banco está vazio. Execute 'scripts/refresh_knowledge.sh' para re-ingerir os documentos."
