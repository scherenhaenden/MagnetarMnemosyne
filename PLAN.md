# Canonical Plan of Magnetar Mnemosyne

This plan captures milestones, tasks, estimates, and status for the project. Its structure must be kept intact.

## Milestones Overview

| Milestone ID | Name | Target Date | Description | Completion Criteria |
| --- | --- | --- | --- | --- |
| `ms-01` | Core Exam Platform Baseline | 2026-05-20 | Stabilize question flows, results tracking, and admin CRUD. | Student and admin flows work end-to-end with passing tests. |
| `ms-02` | Audio Conversation Authoring | 2026-05-27 | Introduce structured listening-scene authoring and admin audio management. | Admin can define multi-speaker scenes and persist them successfully. |
| `ms-03` | Local TTS Rendering Integration | 2026-06-03 | Connect scene definitions to a local AI rendering backend. | Audio scenes can be rendered locally and attached to listening questions. |

## Task Backlog

| Task ID | Milestone | Title | Owner | Effort (pts) | Weight (%) | State | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `task-exam-core-hardening` | `ms-01` | Harden exam flow, DB schema, and CRUD basics | platform | 5 | 21 | `in_review` | Existing tests cover core server flow. |
| `task-audio-scene-schema` | `ms-02` | Define JSON schema for multi-speaker listening scenes | platform | 3 | 13 | `done` | Implemented in `src/audio/conversation_generator.py`. |
| `task-admin-audio-dashboard` | `ms-02` | Add dedicated admin view for audio scene creation | platform | 5 | 21 | `done` | Admin tab `Audios` added. |
| `task-local-tts-runner` | `ms-03` | Implement local render runner for F5-TTS-compatible backend | platform | 8 | 33 | `ready` | Depends on local model path and invocation contract. |
| `task-governance-canon-docs` | `ms-01` | Add canonical governance documents to repository root | platform | 3 | 12 | `done` | Root docs aligned to project context. |

## Effort Summary

- Total effort: `24 pts`
- Completed: `11 pts`
- In progress: `0 pts`
- Remaining: `13 pts`

## State Definitions

- `planned`: identified but not yet prepared for execution
- `ready`: sufficiently defined and unblocked for work to begin
- `in_progress`: actively being implemented
- `blocked`: cannot proceed due to unresolved dependency or impediment
- `in_review`: implemented and waiting for validation, review, or merge
- `done`: accepted, integrated, and documented

## Change Management

This document must be updated whenever tasks change state, ownership, estimate, or scope. Those changes must also be reflected in the project YAML file and logged in `BITACORA.md`.
