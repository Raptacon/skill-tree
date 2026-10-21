# ADR-0002: Google Sheets is the progress store (append-only event log)

- **Status:** Accepted
- **Date:** 2026-10-13
- **Deciders:** Chris Hirsch
- **Supersedes:** README "Phase 2" Go + Postgres backend as the near-term target; `data/students/*.yml` as the progress store

## Context
People data already lives in the Master Roster (Google Sheets), maintained by `raptacon-onboarding-system` (Apps Script): signups, check-in hours, dues balances, background checks, trip paperwork. Keeping progress in git YAML duplicates that data, puts PII in a repo and can't be updated by mentors on the shop floor. A new Go/Postgres service is more than a volunteer team can operate before kickoff.

## Decision
- Progress lives in the mentors-only Master Roster as an **append-only `SkillEvents` tab**, keyed by the roster's Person Key (School ID for students, email for adults). Columns: `event_id, timestamp, season, person_key, item_id, catalog_version, action (complete|revoke|progress), value, verifier_key, method (auto|self|signoff|score|signature), evidence_url, source, notes`.
- Current state is **computed** by Apps Script into a `SkillStatus` snapshot tab. All readers (web app, Python generators) read the snapshot, so the rules are implemented once.
- Writes come only from Forms (sign-off, self-attest, quiz, acknowledgment) and Apps Script derivers. Humans don't edit the log by hand. Corrections are new `revoke`/`complete` events.
- The CI-built item catalog (ids, verify rules, visibility) is published for Apps Script to validate writes against.
- **Derivers, `SkillEvents` and `SkillStatus` live in `Raptacon/raptacon-onboarding-system`** (decided 2026-10-18). It already owns the roster, the clasp deploy pipeline, tests and alerting. This repo publishes the trees and the catalog; it contains no Apps Script.
- `data/students/*.yml` is retired. Example fixtures for tests may remain under `tests/fixtures/`.

## Consequences
- Zero new infrastructure. Uses existing sharing, Forms and Apps Script skills.
- Migration path: `SkillEvents` → Postgres `events` table is a straight copy, and the fold logic ports as-is.
- Depends on `raptacon-onboarding-system` (in git, deployed via clasp since 2026-10-13).
- Sheet-level permissions are coarse. Students and parents never get direct access; they see generated views only.

## Revisit when
Concurrency or latency problems appear, row counts approach ~500k, or we need fine-grained per-user access that Apps Script web apps can't provide.
