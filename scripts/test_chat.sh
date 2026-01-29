#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "🧪 Testando Chat via Terminal..."
echo "👤 Usuário: Quem é Deus?"

if curl -f -N -X POST "http://localhost:8001/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Quem é Deus? Responda em 1 frase."}'; then
    echo -e "\n✅ Fim da resposta."
else
    echo -e "\n❌ Erro ao comunicar com a API."
    exit 1
fi
