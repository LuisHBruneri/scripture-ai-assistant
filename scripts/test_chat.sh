#!/bin/bash
# Navigate to project root
cd "$(dirname "$0")/.."

echo "🧪 Testando Chat via Terminal..."
echo "👤 Usuário: Quem é Deus?"
curl -N -X POST "http://localhost:8001/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Quem é Deus? Responda em 1 frase."}'
echo -e "\n✅ Fim da resposta."
