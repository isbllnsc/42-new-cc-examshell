# 42 Exam Practice Shell

⚡ An interactive practice environment for 42 School exam (Ranks 03) ⚡

## 📋 Overview

This project provides a comprehensive practice shell for 42 School examinations, offering interactive menus and practice exercises for different exam ranks. The shell simulates the actual exam environment and helps students prepare effectively.

## 🚀 Features

- **Interactive Menu System**: Clean, colorful terminal interface
- **Exam Rank 03**: Support for Rank 03 practice exercises
- **Practice Environment**: Dedicated workspace (`rendu` folder) for submissions
- **Command Practice**: Built-in command reference and practice
- **Easy Navigation**: Simple numbered menu system

## 📁 Project Structure

```
.
├── exam.sh           # Main entry point
├── Makefile          # Build configuration
├── README.md         # This file
└── .resources/       # Practice materials
    ├── main/         # Main menu and interface
    ├── rank02/       # Rank 02 exam exercises
    ├── rank03/       # Rank 03 exam exercises
    ├── rank04/       # Rank 04 exam exercises
    ├── rank05/       # Rank 05 exam exercises
    └── rank06/       # Rank 06 exam exercises
```

## 🔧 Installation & Usage

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/terminal-42s/42_examshell
   cd 42_examshell

2. **Run the exam shell**:
   ```bash
   make
   ```
   
   Or directly:
   ```bash
   bash exam.sh
   ```

### Menu Options

The main menu provides the following options:

- **✨ 1. Commands**: Access command reference and practice
- **✨ 2. Exam Rank 03**: Practice exercises for Rank 03 exam
- **✨ 3. Open Rendu Folder**: Access your submission workspace

## 💡 How to Use

1. Launch the application using `make` or `bash exam.sh`
2. Select your desired exam rank or practice option
3. Follow the on-screen instructions
4. Complete exercises in the automatically created `rendu` folder
5. Use the practice environment to simulate real exam conditions

## 📝 Workspace

The shell automatically creates a `rendu` folder where you can:
- Write your solutions
- Test your code
- Practice exam submissions

## 🔄 Staying Up-to-Date

The exam shell includes an automatic update mechanism:

```bash
# Manually run the update script:
bash update.sh
```

The update script will:
- ✅ Check for latest changes from the repository
- ✅ Download and apply all updates automatically
- ✅ Update file permissions for test scripts

Stay tuned for new exam ranks, improved testers, and additional features!

## 🎯 Target Audience

This tool is designed for:
- 42 School students preparing for exams
- Anyone practicing C programming and system administration
- Students wanting to simulate exam conditions

## ⚙️ Requirements

- Bash shell
- Unix-like operating system (Linux/macOS)
- Terminal with color support (recommended)

## 🔄 Updates

The project includes update mechanisms to keep practice materials current with the latest exam requirements.

## 📚 Exam Ranks Covered

- **Rank 03**: Advanced C programming and system calls

## 🤝 Contributing

This is a practice tool for 42 School students. Contributions and improvements are welcome to enhance the learning experience.

## 📧 Support

For issues or questions regarding the practice environment, please refer to your 42 School resources or community.

---

**Good luck with your exams! 🍀**

*Made for 42 School students by isabde-s*
