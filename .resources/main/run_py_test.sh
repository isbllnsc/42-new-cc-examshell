#!/bin/bash
# run_py_test.sh — helper compartilhado para todos os testers do rank03
# Uso: bash run_py_test.sh <QUESTION>
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/colors.sh"

QUESTION="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDU_FILE="${SCRIPT_DIR}/../../rendu/${QUESTION}/${QUESTION}.py"
TEST_FILE="${SCRIPT_DIR}/../../new-common-core/testes-rank-02-python/test_${QUESTION}_42.py"
TRACER_DIR="${SCRIPT_DIR}/../../rendu/tracer/${QUESTION}"

# Verificações
if [ ! -f "$RENDU_FILE" ]; then
    echo -e "${RED}${BOLD}FAIL: arquivo ${QUESTION}.py não encontrado em rendu/${QUESTION}/${RESET}"
    exit 1
fi
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}${BOLD}FAIL: arquivo de teste não encontrado: $TEST_FILE${RESET}"
    exit 1
fi

# Rodar teste
echo -e "${BLUE}Running tests for ${QUESTION}...${RESET}"
output=$(python3 "$TEST_FILE" "$RENDU_FILE" 2>&1)
exit_code=$?

echo "$output"

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}${BOLD}PASSED 🎉${RESET}"
    exit 0
else
    echo -e "${RED}${BOLD}FAIL${RESET}"

    # Salvar no tracer
    mkdir -p "$TRACER_DIR"
    if [ -d "$TRACER_DIR" ]; then
        count=$(find "$TRACER_DIR" -maxdepth 1 -name "*.txt" | wc -l | tr -d ' ')
    else
        count=0
    fi
    tracer_file="${TRACER_DIR}/${count}-${QUESTION}.txt"

    {
        echo "=== Run #${count} ==="
        echo "$output" | grep "^KO:" | sed 's/^KO: /Test: /' | head -1
        echo "$output" | grep "^Expected:" | head -1
        echo "$output" | grep "^Got:" | sed 's/^Got:[[:space:]]*/Your output: /' | head -1
    } > "$tracer_file"

    exit 1
fi
