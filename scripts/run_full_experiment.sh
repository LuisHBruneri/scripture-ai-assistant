#!/bin/bash

# CORES PARA LOGS
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================="
echo -e "   🚀 INICIANDO EXPERIMENTO CIENTÍFICO (TCC)      "
echo -e "==================================================${NC}"
echo -e "Este script executará 3 baterias de testes para validar sua tese."
echo -e "Estima-se que leve entre 40 a 60 minutos (devido a rate limits)."
echo ""

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. TESTE EXPERIMENTAL (AGENTE COMPLETO)
echo -e "${YELLOW}[1/3] Executando Grupo Experimental (Seu Agente)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/agent_report.md
echo -e "${GREEN}✔ Relatório gerado: evaluation/agent_report.md${NC}"
echo ""

# 2. TESTE DE CONTROLE (BASELINE)
echo -e "${YELLOW}[2/3] Executando Grupo de Controle (Baseline)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/baseline_report.md --baseline
echo -e "${GREEN}✔ Relatório gerado: evaluation/baseline_report.md${NC}"
echo ""

# 3. ESTUDO DE ABLAÇÃO (SEM RERANKER)
echo -e "${YELLOW}[3/3] Executando Estudo de Ablação (Sem FlashRank)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/ablation_report.md --no-rerank
echo -e "${GREEN}✔ Relatório gerado: evaluation/ablation_report.md${NC}"
echo ""

echo -e "${BLUE}=================================================="
echo -e "   ✅ EXPERIMENTO CONCLUÍDO COM SUCESSO!          "
echo -e "==================================================${NC}"
echo -e "Arquivos para análise:"
echo -e "1. evaluation/agent_report.md    (Sua Tese)"
echo -e "2. evaluation/baseline_report.md (Comparativo)"
echo -e "3. evaluation/ablation_report.md (Justificativa Técnica)"
echo -e "4. evaluation/results.csv        (Dados Brutos)"
echo ""
