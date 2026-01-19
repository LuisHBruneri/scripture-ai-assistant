#!/bin/bash

echo "📚 Atualizando Base de Conhecimento Teológico..."

# Ensure we are in the root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: Execute este script da raiz do projeto (onde está o docker-compose.yml)."
    exit 1
fi

# Run the ingestion script inside the backend container
docker-compose exec backend python backend/data_ingestion/ingest.py

echo "✅ Concluído! O Agente agora conhece os novos arquivos em 'source_docs'."
