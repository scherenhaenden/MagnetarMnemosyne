# Branching Model for Magnetar Mnemosyne

## Overview

The project uses a lightweight GitFlow-inspired model with a protected `master` branch and short-lived working branches.

## Branch Types

- `master`: release-ready line
- `develop`: optional stabilization line for grouped features
- `feature/*`: new functionality
- `fix/*`: non-emergency bug fixes
- `chore/*`: maintenance and documentation
- `experiment/*`: limited-scope exploratory work
- `hotfix/*`: urgent production fixes from `master`

## Rules

- Branch names must follow `<type>/<short-description>`.
- Rebase feature branches before merge when practical.
- Keep documentation changes with their related code changes.
- Merge only after tests and relevant status artifacts are updated.
