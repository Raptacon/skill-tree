# ADR-0003: Items are a global library; trees are views over them

- **Status:** Proposed (adopt incrementally; onboarding starts inline per ADR-0001)
- **Date:** 2026-10-13

## Context
Overlap between trees is normal: the game rules test is needed by both Drive and Strategy; safety by every tree; the handbook by every role. The current schema puts each skill in exactly one tree, and `hybrids.yml` keeps hand-synced `skills:` lists, which already drift (August follow-ups #5 and #6).

## Decision
- Every item has a **globally unique, stable id**. Ids never change once progress exists against them; renames change `name`, not `id`.
- Shared items live under `items/<area>/`. Trees under `trees/` reference items by id and place them (tier/section), with optional per-tree overrides.
- Prerequisites (`requires`) are edges in one DAG across all trees. CI rejects cycles and unresolved references.
- Hybrids become items whose `requires` spans trees. `hybrids.yml` skill lists are removed (derived instead).
- Items may be inline in a tree file (ADR-0001). The validator treats inline and library items identically, so moving one is a no-op for data.

## Consequences
- Completing the game rules test once counts toward both Drive and Strategy.
- Renderers must handle an item appearing in several trees (show it in each, mark it "shared").
- More files and indirection for authors. Mitigate with a contributor guide, worked examples and a `make new-item` scaffold.
