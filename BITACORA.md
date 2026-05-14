# Logbook of Magnetar Mnemosyne

This document records decisions, state changes, discoveries, and key events in reverse chronological order, with the most recent entry first.

Each entry must use this format:
- `Timestamp:` `YYYY-MM-DD HH:MM Z`
- `Author:` name of the person or AI agent
- `Entry:` concise description of the event

## Entries

---
**Timestamp:** 2026-05-14 14:40 CEST
**Author:** Codex
**Entry:** `task-governance-canon-docs`: state changed from `ready` to `done`. Added canonical governance documents in the repository root and aligned them to Magnetar Mnemosyne.

---
**Timestamp:** 2026-05-14 14:28 CEST
**Author:** Codex
**Entry:** `task-admin-audio-dashboard`: state changed from `in_progress` to `done`. Added dedicated `Audios` tab in the admin dashboard with structured conversation capture and local backend render metadata.

---
**Timestamp:** 2026-05-14 14:22 CEST
**Author:** Codex
**Entry:** Decision: listening-comprehension scenes will be stored as structured JSON payloads with speakers, turns, render metadata, and optional `audio_url`, instead of relying only on raw audio links.

---
**Timestamp:** 2026-05-14 14:05 CEST
**Author:** Codex
**Entry:** Discovery: the repository already supported `audio_listening` questions at the UI layer, but the `src/audio` package was effectively empty and did not yet implement scene generation or TTS orchestration.

## Immutability

This logbook should not be rewritten retroactively. Corrections must be added as new entries that clarify or amend earlier entries.
