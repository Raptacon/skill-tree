# ADR-0001: Onboarding is one tree file with role-tagged items

- **Status:** Accepted (provisional — expected to evolve)
- **Date:** 2026-10-13
- **Deciders:** Chris Hirsch

## Context
Every team member needs onboarding. Onboarding varies by role (student, parent, mentor, volunteer, board), and roles overlap heavily: the handbook, the signup form and Discord apply to everyone; safety applies to students and mentors. One person can hold several roles (parent + mentor + board). The alternatives were one file per role (duplicates shared items) or a shared-library-plus-views model (more structure than we need on day one).

## Decision
- One file, `trees/onboarding.yml`, with items defined inline. Each item carries `roles: [...]`.
- Roles are formally defined in `roles.yml` (id, name, description, how membership is determined from the roster).
- Renderers produce a separate view per role. A person holding several roles sees the **union**, de-duplicated by item id.
- Conditional items use `when:` (e.g. `ccsd_volunteer`, `chaperone`) rather than inventing new roles.

## Consequences
- Simple to author and review. One PR touches one file.
- Works with ADR-0003: inline items can later move to `items/common/` and be referenced, with no change to item ids or recorded progress.
- Role-specific nuance (e.g. "parent signs the FIRST consent *for* the student") must be expressible per item. Use `roles` + `description`, plus a `for_role` link where the action belongs to a different role than the requirement.

## Revisit when
Item count passes ~40, or more than ~5 items are duplicated across other trees.
