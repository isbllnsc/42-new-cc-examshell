#!/bin/bash
source colors.sh

rank=$1
level=$2

# Save base directory (where script was launched from)
base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Centralized temp file to track subject
subject_file="/tmp/.current_subject_${rank}_${level}"

# Define subject pool
get_subjects() {
    case "$level" in
        level0)
            echo "bracket_validator count_consecutive_digit_pairs crypto_sorter echo_validator merge_sorted_lists mirror_matrix number_base_converter pattern_tracker permutation_checker twist_permutation whisper_cipher"
            ;;
        *)
            echo ""
            ;;
    esac
}

pick_new_subject() {
    subjects_list=$(get_subjects)
    IFS=' ' read -r -a qsub <<< "$subjects_list"
    count=${#qsub[@]}
    random_index=$(( RANDOM % count ))
    chosen="${qsub[$random_index]}"
    echo "$chosen" > "$subject_file"
}

prepare_subject() {
    # Create rendu directory and the Python file for the user
    mkdir -p "$base_dir/../../rendu/$chosen"
    touch "$base_dir/../../rendu/$chosen/$chosen.py"

    cd "$base_dir/../$rank/$level/$chosen" || {
        echo -e "${RED}Subject folder not found.${RESET}"
        exit 1
    }

    clear
    echo -e "${CYAN}${BOLD}🐍 Your subject: $chosen${RESET}"
    echo "=================================================="
    cat sub.txt
    echo
    echo "=================================================="
    echo -e "${YELLOW}Your file: rendu/$chosen/$chosen.py${RESET}"
    echo -e "${YELLOW}Type 'test' to test your code, 'next' to get a new question, or 'exit' to quit.${RESET}"
}

# Initial subject selection
if [ -f "$subject_file" ]; then
    chosen=$(cat "$subject_file")
    echo -e "${BLUE}🔁 Resuming with previously chosen subject: $chosen${RESET}"
else
    pick_new_subject
    chosen=$(cat "$subject_file")
fi

prepare_subject

# Command loop
while true; do
    read -rp "/> " input
    case "$input" in
        test)
            clear
            echo -e "${GREEN}Running tester...${RESET}"
            output=$(bash tester.sh 2>&1)
            echo "$output" | tee tester_output.log

            if echo "$output" | grep -q -E "PASSED|SUCCESS|OK:"; then
                echo -e "${GREEN}${BOLD}✔️  Passed!${RESET}"
                rm -f "$subject_file"
                sleep 1
                exit 0
            else
                echo -e "${RED}${BOLD}❌  Failed.${RESET}"
                sleep 1
                exit 1
            fi
            ;;
        next)
            echo -e "${BLUE}🔄 Picking a new subject...${RESET}"
            pick_new_subject
            chosen=$(cat "$subject_file")
            prepare_subject
            ;;
        exit)
            echo "Exiting..."
            rm -f "$subject_file"
            exit 0
            ;;
        *)
            echo "Please type 'test' to test code, 'next' for next or 'exit' to quit."
            ;;
    esac
done
