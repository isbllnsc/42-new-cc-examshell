#!/bin/bash
source colors.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACER_BASE="${SCRIPT_DIR}/../../rendu/tracer"

QUESTIONS=(
    bracket_validator
    count_consecutive_digit_pairs
    crypto_sorter
    echo_validator
    merge_sorted_lists
    mirror_matrix
    number_base_converter
    pattern_tracker
    permutation_checker
    twist_permutation
    whisper_cipher
)

show_main_menu() {
    clear
    bash label.sh
    printf "${WHITE}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
    printf "${WHITE}║${GREEN}          🧩 RANK 03 PYTHON - TEST TRACER (VIEWER)         ${WHITE}║${RESET}\n"
    printf "${WHITE}%s${RESET}\n" "╠═══════════════════════════════════════════════════════════╣"

    # Verifica se existe algum histórico
    has_any=0
    for q in "${QUESTIONS[@]}"; do
        if [ -d "${TRACER_BASE}/${q}" ] && ls "${TRACER_BASE}/${q}"/*.txt 2>/dev/null | grep -q .; then
            has_any=1
            break
        fi
    done

    if [ $has_any -eq 0 ]; then
        echo
        printf "${WHITE}  Nenhum teste foi executado ainda.${RESET}\n"
        printf "${WHITE}  Execute uma questão com o comando ${GREEN}test${WHITE} para gerar histórico.${RESET}\n"
        echo
        printf "${WHITE}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
        printf "${GREEN}${BOLD}Pressione Enter para voltar...${RESET}"
        read -r
        bash rank02py_menu.sh
        exit
    fi

    printf "${WHITE}${BOLD}  Questões com histórico de testes:${RESET}\n"
    printf "${WHITE}%s${RESET}\n" "───────────────────────────────────────────────────────────"

    local i=1
    local indexed=()
    for q in "${QUESTIONS[@]}"; do
        if [ -d "${TRACER_BASE}/${q}" ] && ls "${TRACER_BASE}/${q}"/*.txt 2>/dev/null | grep -q .; then
            count=$(ls "${TRACER_BASE}/${q}"/*.txt 2>/dev/null | wc -l | tr -d ' ')
            printf "${WHITE}${BOLD}  %2d. %-40s ${GREEN}(%s run(s))${RESET}\n" "$i" "$q" "$count"
            indexed+=("$q")
            i=$((i + 1))
        fi
    done

    printf "${WHITE}%s${RESET}\n" "───────────────────────────────────────────────────────────"
    printf "${WHITE}${BOLD}   0. Back to Rank 03 Menu${RESET}\n"
    printf "${GREEN}${BOLD}Enter your choice: ${RESET}"

    read -r choice
    if [ "$choice" = "0" ]; then
        bash rank02py_menu.sh
        exit
    fi

    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#indexed[@]}" ]; then
        echo -e "${RED}Escolha inválida.${RESET}"
        sleep 1
        show_main_menu
        return
    fi

    show_question_history "${indexed[$((choice - 1))]}"
}

show_question_history() {
    local q="$1"
    local q_tracer="${TRACER_BASE}/${q}"

    clear
    bash label.sh
    printf "${WHITE}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
    printf "${WHITE}║  ${GREEN}🧩 TRACER: ${q}${RESET}\n"
    printf "${WHITE}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
    echo

    local files
    files=$(ls -v "${q_tracer}"/*.txt 2>/dev/null)
    local total
    total=$(echo "$files" | wc -l | tr -d ' ')

    printf "${WHITE}${BOLD}  %s runs registrados para '${q}':${RESET}\n" "$total"
    echo

    local run_num=0
    while IFS= read -r f; do
        run_num=$((run_num + 1))
        if [ "$run_num" -eq "$total" ]; then
            # Último run — destaque em vermelho (é o que não passou)
            printf "${RED}${BOLD}  ── Run #%d (último) ──────────────────────────────────${RESET}\n" "$((run_num - 1))"
            while IFS= read -r line; do
                printf "${RED}  %s${RESET}\n" "$line"
            done < "$f"
        else
            printf "${WHITE}  ── Run #%d ────────────────────────────────────────────${RESET}\n" "$((run_num - 1))"
            while IFS= read -r line; do
                printf "${WHITE}  %s${RESET}\n" "$line"
            done < "$f"
        fi
        echo
    done <<< "$files"

    printf "${WHITE}%s${RESET}\n" "───────────────────────────────────────────────────────────"
    printf "${GREEN}${BOLD}Pressione Enter para voltar...${RESET}"
    read -r
    show_main_menu
}

# Loop principal
show_main_menu
