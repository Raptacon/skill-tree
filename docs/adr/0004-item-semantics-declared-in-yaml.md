# ADR-0004: Verification, renewal, visibility and kind are declared per item in YAML

- **Status:** Accepted
- **Date:** 2026-10-13

## Context
How an item is verified (auto, self, sign-off by a role or a specific person, score, signature) and whether it renews (annually vs. kept once earned) varies per item. So does who may see someone's status. The old schema set verification per *tier* (`tiers.yml`), which can't express onboarding or shared items.

## Decision
Every item declares:
- `kind`: `check | count | hours | score | signature | external`, plus kind-specific fields (`target`, `pass_score`, …)
- `verify`: `method` (`auto | self | signoff | score | signature`) + `by` (`{role: x}`, `{person: "@github-handle"}`, or `any_of` / `all_of` combinations) + `source` for auto
- `renews`: `season | permanent | event` (per trip/event) | `{months: N}`
- `visibility`: `public | team | mentors | self`. CI forbids `public` on sensitive categories
- `requires`: item ids and/or thresholds (`{hours: 150}`, `{tree: x, tier: n}`)

Tier-level defaults in `tiers.yml` remain as **defaults** that items inherit and can override.

**Authorship metadata** (added 2026-10-13): trees and items carry `authored_by: [{name, github}]` (first + last name for credit, no emails), `created_at` and `updated_at`.

**People in YAML** are only ever `{name, github}`. Items reference *roles*; `assignments.yml` maps roles to people per season. The site and checklists can then say "ask Jane D. or Sam K." while a lead change stays a one-line PR. Items may also carry `practical: {summary, steps}`, the exact hands-on task a verifier runs. Trees set defaults and items override. These are kept in YAML instead of being derived from `git blame` because blame loses track when items move between files (ADR-0003). CI keeps `updated_at` honest by failing a PR that edits an item without bumping it.

Scoped sign-off roles use `{role: <id>, tree: <tree-id>}` (e.g. `{role: subteam-lead, tree: manufacturing}`).

## Consequences
- Apps Script enforces `verify.by` on sign-off writes using the published catalog.
- Specific-person sign-off uses GitHub handles (public, already in the roster) rather than emails, to keep PII out of the repo.
- A season boundary must be defined once, centrally (open question in requirements §6).
