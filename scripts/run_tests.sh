#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
ALLURE_RESULTS_DIR="${ALLURE_RESULTS_DIR:-allure/results}"
OPEN_ALLURE="${OPEN_ALLURE:-true}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python do projeto nao encontrado em: $PYTHON_BIN"
  echo "Crie o virtualenv e instale as dependencias:"
  echo "  python3.12 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

mkdir -p "$ALLURE_RESULTS_DIR"

"$PYTHON_BIN" -m pytest tests -v --alluredir="$ALLURE_RESULTS_DIR" --clean-alluredir

if [[ "$OPEN_ALLURE" == "true" ]]; then
  if ! command -v allure >/dev/null 2>&1; then
    echo "Testes executados, mas o comando 'allure' nao foi encontrado no PATH."
    echo "Instale o Allure CLI para abrir o relatorio com:"
    echo "  allure serve $ALLURE_RESULTS_DIR"
    exit 1
  fi

  allure serve "$ALLURE_RESULTS_DIR"
else
  echo "Relatorio Allure gerado em: $ALLURE_RESULTS_DIR"
fi
