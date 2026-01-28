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

# Parar se qualquer comando falhar
set -e

# Função de erro
trap 'echo -e "${YELLOW}❌ O teste foi interrompido ou falhou.${NC}"; exit 1' INT ABRT TERM ERR

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start Global Timer
START_TIME=$SECONDS

function print_progress() {
    local step=$1
    local total_steps=3
    local percent=$(( step * 100 / total_steps ))
    local elapsed=$(( SECONDS - START_TIME ))
    local minutes=$(( elapsed / 60 ))
    local seconds=$(( elapsed % 60 ))
    
    echo ""
    echo -e "${BLUE}--------------------------------------------------${NC}"
    echo -e "${GREEN}✅ PROGRESSO GLOBAL: ${percent}% Concluído${NC}"
    echo -e "🕒 Tempo Decorrido: ${minutes}m ${seconds}s"
    echo -e "${BLUE}--------------------------------------------------${NC}"
    echo ""
}

# 1. TESTE EXPERIMENTAL (AGENTE COMPLETO)
echo -e "${YELLOW}[1/3] Executando Grupo Experimental (Seu Agente)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/agent_report.md
print_progress 1

# 2. TESTE DE CONTROLE (BASELINE)
echo -e "${YELLOW}[2/3] Executando Grupo de Controle (Baseline)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/baseline_report.md --baseline
print_progress 2

# 3. ESTUDO DE ABLAÇÃO (SEM RERANKER)
echo -e "${YELLOW}[3/3] Executando Estudo de Ablação (Sem FlashRank)...${NC}"
"$SCRIPT_DIR/run_validation.sh" --dataset evaluation/advanced_dataset.json --output evaluation/ablation_report.md --no-rerank
print_progress 3

echo -e "${BLUE}=================================================="
echo -e "   ✅ EXPERIMENTO CONCLUÍDO COM SUCESSO!          "
echo -e "==================================================${NC}"
TOTAL_TIME=$(( SECONDS - START_TIME ))
echo -e "🏁 Tempo Total: $(( TOTAL_TIME / 60 ))m $(( TOTAL_TIME % 60 ))s"
echo -e "Arquivos para análise:"
echo -e "1. evaluation/agent_report.md    (Sua Tese)"
echo -e "2. evaluation/baseline_report.md (Comparativo)"
echo -e "3. evaluation/ablation_report.md (Justificativa Técnica)"
echo -e "4. evaluation/results.csv        (Dados Brutos)"
echo ""
