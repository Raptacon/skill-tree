# ADR-0006: The roster is the source of truth for team membership and roles

- **Status:** Accepted
- **Date:** 2026-10-20
- **Deciders:** Chris Hirsch

## Context
Nothing authoritative says who is on which subteam, or who leads or mentors it. The roster's `Sub-team Interest` columns are sign-up-form interest and are never updated. Discord subteam roles are self-selected. `assignments.yml` is accurate but hand-edited and covers only the people who sign off. The site needs "ask Emma"; Clutch (the team Discord bot) and planned GitHub teams need membership too.

## Decision
- **The Master Roster is the single source of truth.** Discord roles, GitHub teams and this repo's `assignments.yml` are generated from it, never the other way round.
- **Primary subteam** = the subteam whose lead signed `base-choose-track`. Until sign-offs are recorded in `SkillEvents`, mentors maintain a `Subteams` column in the roster.
- **Leads, subteam mentors and other sign-off roles** live in a roster `Roles` tab (season, role, subteam, person, GitHub username), maintained by mentors.
- **One-time seed:** Clutch proposes `Subteams` values from current self-selected Discord roles, a mentor confirms them, and Discord stops being a source.
- **This repo** receives an export of the `Roles` tab (name + GitHub username only) and CI generates `assignments.yml` from it. Until then, `assignments.yml` is edited by hand.

## Consequences
- One place to change when a lead or mentor changes mid-season.
- The roster work (schema, Clutch sync, export) lives in `raptacon-onboarding-system` (see ADR-0002).
- No personal data enters this repo: the export carries names and GitHub usernames only.
