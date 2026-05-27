#!/bin/bash
source colors.sh

clear
bash label.sh
printf "${WHITE}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
printf "${GREEN}║            🐍 EXAM RANK 03 - MODE SELECTION 🐍            ║${RESET}\n"
printf "${WHITE}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${WHITE}%s${RESET}\n" "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 1. Level Mode"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 2. Real Exam Mode"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 3. Tracer"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 4. Back to Main Menu"
printf "${WHITE}%s${RESET}\n" "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${WHITE}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
printf "${GREEN}${BOLD}Enter your choice (1-4): ${RESET}"
read rank02py_opt
case $rank02py_opt in
    1)
        bash rank02py.sh
        ;;
    2)
        bash rank02py_real_mode.sh
        ;;
    3)
        bash rank02py_tracer.sh
        ;;
    4)
        bash intro.sh
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, 3, or 4."
        sleep 1
        bash rank02py_menu.sh
        ;;
esac
