#!/bin/bash
source functions.sh
source colors.sh

run_level() {
    level=$1
    clear
    echo "$(tput setaf 2)$(tput bold)🐍 Python Level $level is being prepared...$(tput sgr0)"
    display_animation
    clear
    until bash rank02py_exam_mode.sh rank02py level$level; do
        echo "$(tput setaf 1)Test failed. Try again.$(tput sgr0)"
        read -p "Press Enter to retry Level $level..."
        clear
    done
    echo "$(tput setaf 2)✔️  Level $level passed!$(tput sgr0)"
    sleep 1
}

start_exam() {
    clear
    bash label.sh
    echo "$(tput setaf 2)$(tput bold)🐍 Welcome to the Rank02 Python Exam!$(tput sgr0)"
    echo "=================================================="
    sleep 1

    mkdir -p ../../rendu
    run_level 0

    clear
    echo "$(tput setaf 2)$(tput bold)🎉 Congratulations! You've completed Rank02 Python!$(tput sgr0)"
    echo "=================================================="
    echo "All levels passed successfully!"
    sleep 3
}

start_exam
