source colors.sh
mkdir -p ../../rendu
clear
bash label.sh
printf "${WHITE}%s${RESET}\n" "╔═══════════════════════════════════════════════════════════╗"
printf "${GREEN}║          🐍 EXAM 42 PRACTICE TEST - MAIN MENU 🐍          ║${RESET}\n"
printf "${WHITE}%s${RESET}\n" "╠═══════════════════════════════════════════════════════════╣"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${WHITE}%s${RESET}\n" "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 1. Commands"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 2. Exam Rank 03"
printf "${WHITE}${BOLD}%s${RESET}\n" "✨ 3. Open Rendu Folder"
printf "${WHITE}%s${RESET}\n" "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆"
printf "${BLUE}%s${RESET}\n" "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
printf "${WHITE}%s${RESET}\n" "╚═══════════════════════════════════════════════════════════╝"
printf "${GREEN}${BOLD}Enter your choice (1-3): ${RESET}"
read opt
case $opt in
    1)
        bash help.sh
        ;;
    2)
        bash rank02py_menu.sh
        ;;
    3)
        cd ../../rendu
        open .
        cd ../.resources/main
        bash menu.sh
        exit 1
        ;;
    exit)
        cd ../../../../
        rm -rf rendu
        clear
        exit 1
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, or 3."
        sleep 1
        clear
        bash menu.sh
esac
