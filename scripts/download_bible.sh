#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "📖 Baixando Bíblia..."
python3 backend/data_ingestion/download_bible.py
echo "✅ Download concluído! Execute 'scripts/refresh_knowledge.sh' para importar."
