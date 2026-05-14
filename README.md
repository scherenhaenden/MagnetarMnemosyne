# 🧠 Magnetar Mnemosyne - Exam System

A highly interactive, modular, and resilient exam management system built with **Python**, **FastAPI**, and **HTMX**.

![Project Status](https://img.shields.io/badge/Status-Development-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 🚀 Overview

Magnetar Mnemosyne is an "auto-healing" application designed to create and manage complex educational assessments. It features a seamless student interface and a powerful administrative dashboard.

### Key Capabilities:
- **Multiple Question Types**: 
    - **Multiple Choice**: Standard MCQ with immediate feedback.
    - **Long Text**: Detailed text responses with auto-save.
    - **Audio Listening**: Integrated player for "listen and write" assessments.
- **Advanced Exam Management**:
    - Create and group questions into specific exams (e.g., "Basic Math", "History 101").
    - Edit and update existing exams dynamically.
- **Results Tracking**: Comprehensive database of student attempts, scores, and completion dates.
- **Dynamic Dependency Management**: Auto-installs missing packages (FastAPI, UV, etc.) at runtime.
- **Interactive UI**: SPA-like experience powered by HTMX, supporting both Dark and Light themes.

---

## 🛠️ Installation & Quick Start

### 1. Prerequisites
- Python 3.10+
- `uv` (Recommended for high-performance dependency management)

### 2. Running the Application
The system is **Zero-Config**. Running the main script handles environment setup and database migration.

```bash
# Using standard Python
python3 main.py

# Using UV (Recommended)
uv run main.py
```

- **Student Interface**: [http://localhost:8000](http://localhost:8000)
- **Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 📂 Project Structure

```text
.
├── main.py               # Main entry point (starts the server)
├── run_tests.py          # Coverage-enabled test runner
├── src/
│   ├── ui/               # FastAPI Server & Jinja2 Templates
│   ├── exams/            # SQLite Database (questions, exams, results)
│   └── utils/            # Dependency Manager (Auto-healer)
├── tests/                # Comprehensive Pytest suite
└── docs/                 # Detailed documentation
```

---

## ⚙️ Core Features

### 📊 Admin Dashboard
- **Exams Management**: Create, edit, and view specific exams and their contents.
- **Question CRUD**: Full management of the question bank.
- **Bulk JSON Import**: Rapidly populate the database by pasting JSON question sets.
- **Results View**: Monitor student performance with a detailed grading table.

### 📝 Student Experience
- **Exam Selection**: Students choose their name and assigned exam from a central portal.
- **Auto-Save**: Text and audio responses are saved in real-time as the student types.
- **Hybrid Feedback**: Choose between interactive (live correction) and classic (end-of-exam summary) modes.

---

## 🧪 Testing & Quality
The project targets **100% test coverage** for maximum reliability.

```bash
python3 run_tests.py
```

---

## 📖 Detailed Documentation
For more in-depth information, please refer to:
- [Architecture & Design](./docs/ARCHITECTURE.md)
- [User Guide & JSON Import](./docs/USAGE.md)
- [Development & Contribution](./docs/DEVELOPMENT.md)
