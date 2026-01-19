#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "📚 Atualizando Base de Conhecimento Teológico..."

# Run the ingestion script inside the backend container
docker-compose exec backend python backend/data_ingestion/ingest.py

echo "✅ Concluído! O Agente agora conhece os novos arquivos em 'source_docs'."
