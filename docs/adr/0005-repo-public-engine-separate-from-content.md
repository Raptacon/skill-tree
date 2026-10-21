# ADR-0005: Make the repo public, with no people data, and keep the engine separable from content

- **Status:** Accepted (2026-10-18): public once `main` has the CI pipeline (YAML validation, personal-data lint, site build).
- **Date:** 2026-10-13

## Context
`Raptacon/skill-tree` is currently **private**. The goal is for other FRC teams to be able to fork it eventually, and for the whole team (students included) to contribute. Nothing in the tree definitions is secret once people data lives in Sheets (ADR-0002).

## Decision
- Flip to **public** once these guardrails exist:
  - CI PII lint (no emails, phone numbers or 8-digit IDs in YAML)
  - generated outputs gitignored
  - `data/students/` removed
  - git history scanned
  - linked Google Docs' sharing settings audited
- Repo layout separates **engine** (`schema/`, `validator`, `generators/`, Apps Script) from **team content** (`content/raptacon/{roles,items,trees}`), so another team can swap the content directory, and a later split into engine + template repos is mechanical.
- Add a LICENSE: MIT/Apache-2.0 for code, CC BY-SA for content (to confirm).

## Consequences
- Enables forking, recruiting/Impact narrative, student portfolio credit.
- Requires discipline: anything sensitive goes in Sheets or private Drive, never in the repo.

## Alternatives
- Stay private until "worthy," then open it. Rejected because it risks a history scrub later, and because the guardrails are cheap now.
