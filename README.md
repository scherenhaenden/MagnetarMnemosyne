# Canonical Project Model of Magnetar Mnemosyne

Magnetar Mnemosyne exists to build and operate a modular exam platform with special emphasis on language assessments, listening-comprehension workflows, and admin-controlled audio generation. The repository combines product code with a Magnetar-style operating model for documentation, planning, and governance so that delivery, decisions, and risks stay auditable.

## Purpose

The project solves two related problems:
- delivering browser-based exams with multiple question types, results tracking, and exam administration
- managing the work around that product using a consistent canon for planning, blockers, testing, and project state

This repository follows the Magnetar standard for documentation, planning, and governance while keeping `Magnetar Mnemosyne` as the actual product identity.

## How to Use This Repository

1. Clone the canonical model in its adapted form by cloning this repository.
2. Copy and fill out [projects/_template.project.yml](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/projects/_template.project.yml:1) for each concrete project instance or stream of work.
3. Replicate the required documentation set in the project root and keep those files aligned with implementation.
4. Follow the WIP, branching, and blocker rules defined in [WIP_GUIDELINES.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/WIP_GUIDELINES.md:1), [BRANCHING_MODEL.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BRANCHING_MODEL.md:1), and [BLOCKERS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BLOCKERS.md:1).
5. Consult the example project artifacts in this repository when a process, format, or status transition is unclear.

## Project Contents

| File | Purpose |
| --- | --- |
| `PLAN.md` | Project tasks, estimates, milestones, and state tracking. |
| `BITACORA.md` | Reverse-chronological logbook of decisions, changes, and discoveries. |
| `REQUIREMENTS.md` | Functional and non-functional requirements. |
| `ARCHITECTURE.md` | High-level system and module structure. |
| `RULES.md` | Naming rules, workflow standards, and compliance constraints. |
| `STATUS.md` | Health summary, progress snapshot, and active risks. |
| `TESTING.md` | Testing strategy, coverage targets, and bug reporting rules. |
| `BLOCKERS.md` | Active and resolved blockers plus escalation flow. |
| `BRANCHING_MODEL.md` | Governance reference for branches, merge readiness, and release flow. |
| `WIP_GUIDELINES.md` | Governance reference for concurrency limits and exception handling. |

## Progress Model Overview

Progress is tracked through milestones and tasks that move across the approved states: `planned` -> `in_progress` -> `in_review` -> `done`. Supporting states such as `ready` and `blocked` exist for queueing and interruption control. Every state change must be reflected in [PLAN.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/PLAN.md:1) and recorded in [BITACORA.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BITACORA.md:1).

## YAML Project Schema

The file [projects/_template.project.yml](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/projects/_template.project.yml:1) defines the canonical machine-readable schema used by humans and AI collaborators. It contains project metadata, stakeholders, milestones, tasks, risks, and reporting configuration.

## Guidance for AI Collaborators

AI collaborators must:
- parse the project YAML file before acting on planning-sensitive work
- use [PLAN.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/PLAN.md:1) and [STATUS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/STATUS.md:1) to determine current focus
- respect [RULES.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/RULES.md:1), [WIP_GUIDELINES.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/WIP_GUIDELINES.md:1), and [BRANCHING_MODEL.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BRANCHING_MODEL.md:1)
- update [BITACORA.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BITACORA.md:1) after completing meaningful work, changing assumptions, or resolving blockers

## Architecture Diagram

```text
RULES / BRANCHING / WIP
          |
          v
       PLAN.md
          |
          v
  IMPLEMENTATION + TESTING
          |
          v
 STATUS / BITACORA / BLOCKERS
          |
          v
   EXAMPLE PROJECT RECORD
```

## Applying This Template

1. Copy the repository structure.
2. Replace placeholder content with project-specific details for the actual product and delivery stream.
3. Instantiate and validate a project YAML file under `projects/`.
4. Establish initial milestones and log the initial state in `PLAN.md`, `STATUS.md`, and `BITACORA.md`.

## Validating Canon Compliance

- Confirm that all required governance files exist.
- Confirm that the project YAML matches the expected schema and naming rules.
- Confirm that `BITACORA.md` is updated chronologically, most recent first.
- Confirm that active branches follow [BRANCHING_MODEL.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BRANCHING_MODEL.md:1).
- Confirm that testing and blocker handling match [TESTING.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/TESTING.md:1) and [BLOCKERS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/BLOCKERS.md:1).

## Product Runtime

The product itself is a Python, FastAPI, HTMX, and SQLite exam system with support for multiple-choice, long-text, and audio-listening questions. The admin dashboard now includes audio-scene management for conversation-driven language tests.

```bash
python3 main.py
```

- Student interface: `http://localhost:8000`
- Admin dashboard: `http://localhost:8000/admin`

## Audio Backends

The admin dashboard supports interchangeable local audio backends for listening scenes:
- `F5-TTS`
- `Kokoro`

Configuration is centralized in [appsettings.json](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/appsettings.json:1).

User-facing documentation:
- [docs/USAGE.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/USAGE.md:1)
- [docs/AUDIOS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/AUDIOS.md:1)

Developer-facing documentation:
- [docs/DEVELOPMENT.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/DEVELOPMENT.md:1)
- [docs/ARCHITECTURE.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/ARCHITECTURE.md:1)
