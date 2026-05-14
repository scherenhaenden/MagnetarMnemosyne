# 🧠 Magnetar Mnemosyne - Exam System

A highly interactive, modular, and resilient exam management system built with **Python**, **FastAPI**, and **HTMX**.

![Project Status](https://img.shields.io/badge/Status-Development-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 🚀 Overview

Magnetar Mnemosyne is an "auto-healing" application designed to create and manage complex exams. It supports:
- **Multiple Choice Questions** (MCQ)
- **Long Text Answers**
- **Dynamic Dependency Management** (Auto-installs missing packages at runtime)
- **Interactive Student UI** (FastAPI + HTMX for a SPA-like experience)
- **Admin Dashboard** with SQLite persistence and JSON bulk import.

---

## 🛠️ Installation & Quick Start

### 1. Prerequisites
- Python 3.10+
- `uv` (Optional, but highly recommended for speed)

### 2. Running the Application
The system is designed to be **Zero-Config**. Simply run the main script, and it will handle everything from dependencies to database initialization.

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
│   ├── exams/            # SQLite Database logic & Question management
│   └── utils/            # Dependency Manager (Auto-healer)
├── tests/                # Comprehensive Pytest suite
└── docs/                 # Detailed documentation
```

---

## ⚙️ Core Features

### 🛡️ Auto-Healing Dependency Manager
The application monitors its own environment. If an import fails, it detects your environment (Standard Pip or UV) and installs the required package **on-the-fly** before continuing execution.

### 📊 Admin Dashboard
- **CRUD Operations**: Add and delete questions manually.
- **Bulk JSON Import**: Paste complex question sets in JSON format to populate the database instantly.
- **Dark/Light Mode**: Default dark theme with a toggle for accessibility.

### 📝 Interactive Exams
- **Live Feedback Mode**: Correct answers and explanations are shown immediately after selection.
- **Classic Mode**: Results are summarized only at the end of the exam.
- **HTMX Powered**: Smooth transitions without full page reloads.

---

## 🧪 Testing & Quality
We aim for high reliability. The project includes a full suite of tests with coverage reporting.

```bash
python3 run_tests.py
```

---

## 📖 Detailed Documentation
For more in-depth information, please refer to:
- [Architecture & Design](./docs/ARCHITECTURE.md)
- [User Guide & JSON Import](./docs/USAGE.md)
- [Development & Contribution](./docs/DEVELOPMENT.md)
