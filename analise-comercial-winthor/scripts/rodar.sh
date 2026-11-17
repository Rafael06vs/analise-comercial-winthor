#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
{
  echo "Início: $(date -Is)"
  python3 scripts/gerar_dados.py
  rm -f dados/analise.db
  python3 scripts/analisar.py
  echo "Fim: $(date -Is)"
} 2>&1 | tee -a logs/execucao.log
