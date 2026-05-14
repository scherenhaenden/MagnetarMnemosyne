# Canonical Ruleset of Magnetar Mnemosyne

## Introduction

These rules codify the Magnetar standard as adapted for Magnetar Mnemosyne. The entire project must comply unless a formal exception is explicitly documented in `BITACORA.md`.

## Naming Conventions

- Repositories: `magnetar-<domain>-<descriptor>` for canon-aligned repos in general; this repository keeps the established product name `MagnetarMnemosyne`.
- Branches: `<type>/<short-description>` where `type` is `feature`, `fix`, `chore`, `experiment`, or `hotfix`.
- Tasks and blockers: `kebab-case`, for example `task-audio-render-runner` or `blocker-local-model-missing`.
- YAML keys: `lower_snake_case`.
- File names: governance files must mirror the canonical names defined in this repository.

## Required Files

Every Magnetar-governed project must include:
- `README.md`
- `PLAN.md`
- `BITACORA.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `RULES.md`
- `STATUS.md`
- `TESTING.md`
- `BLOCKERS.md`
- `BRANCHING_MODEL.md`
- `WIP_GUIDELINES.md`
- `CONTRIBUTING.md`
- `projects/<project>.project.yml`

Any omission requires an explicit exemption logged in `BITACORA.md`.

## Branching Conventions

- `master`: immutable release line; merges require successful CI, aligned docs, and updated status artifacts.
- `develop`: optional aggregation branch for completed features before stabilization.
- `feature/*`: branch from `master` or `develop` and rebase before merge.
- `hotfix/*`: branch from `master`; completion must trigger a `STATUS.md` update.
- Every pull request must reference the tasks it affects and include corresponding `BITACORA.md` entries.

## Allowed Task States

1. `planned`
2. `ready`
3. `in_progress`
4. `in_review`
5. `blocked`
6. `done`

Allowed transitions:
- `planned` -> `ready` when scope is accepted
- `ready` -> `in_progress` when work begins
- `in_progress` -> `in_review` when implementation is complete and awaiting validation
- `in_review` -> `done` when accepted and merged
- any active state -> `blocked` when an impediment prevents normal progress
- `blocked` -> `ready` or `in_progress` when the impediment is resolved

## Work-In-Progress Constraints

- WIP limit: no individual human or AI agent should own more than two `in_progress` tasks at once.
- Exceptions: exceeding the limit requires explicit approval and must be documented in `WIP_GUIDELINES.md` and `BITACORA.md`.

## Blocker Lifecycle

1. Discovery: log the blocker in `BLOCKERS.md` with ID, description, severity, owner, and timestamp.
2. Assessment: update risks in `STATUS.md` and note mitigation ideas in `BITACORA.md`.
3. Escalation: escalate if unresolved within one business day or if it blocks a release-critical path.
4. Resolution: document the solution steps in `BITACORA.md` and mark the blocker as resolved.
5. Retrospective: capture lessons learned and any process changes needed.

## Documentation Discipline

- `BITACORA.md` must chronologically record every state change, decision, or documented exception.
- `STATUS.md` must be updated at least once per day during active work or after each merged PR.
- `PLAN.md` is the source of truth for milestones, tasks, and ownership.

## AI Agent Responsibilities

- Parse the project YAML file before acting on planning or status-sensitive work.
- Do not open PRs unless the relevant task is already in `in_review`.
- Document assumptions in `BITACORA.md` when uncertainty materially affects implementation or delivery.

## Compliance and Enforcement

- CI should validate the presence and minimum structure of required governance files.
- Periodic audits should verify state consistency across `PLAN.md`, project YAML, `STATUS.md`, and `BITACORA.md`.
