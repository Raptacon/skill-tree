# Raptacon Skill Tree

Raptacon 3200's gamified skill-tree progression system. This repo is **Phase 1**: a schema-driven set of generators that turn plain YAML into a printable tree poster and a per-student progress one-pager.

Phase 2 (a real system of record — check-ins, verifications, a live app) is documented at the bottom of this README but not built yet. This repo's YAML files are designed so that migration is a straight import, not a rewrite.

## Setup

```bash
pipenv install
```

## Usage

```bash
make poster TREE=manufacturing     # writes tmp/manufacturing_poster.html
make onepager STUDENT=example      # writes tmp/example_onepager.html
make techmap                       # writes tmp/techmap.html - the whole program in one picture
make validate                      # checks all data/*.yml parses
```

Trees available for `TREE=`: `manufacturing`, `design`, `electronics`, `programming`, `business`, `leds` (`baseline` isn't tiered, so it doesn't have its own poster — it shows up as the banner strip at the top of `techmap`). Students available for `STUDENT=`: `example`, `firstname_lastname`.

Open the generated HTML in Chrome (or any modern browser) to view or print it. Headless-render a PNG for a quick look without opening a window:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new --disable-gpu --window-size=850,1400 \
  --screenshot=tmp/manufacturing_poster.png \
  "file://$PWD/tmp/manufacturing_poster.html"
```

## Schema

Everything lives under `data/` as YAML — this is the single source of truth for both generators (and, later, for seeding Phase 2's database).

- **`data/trees.yml`** — registry of skill trees: `{id, name, tiered, kind, parent_trees?}`. `tiered: false` (currently just `baseline`) means a flat pass/fail checklist with no tier ladder. `kind: subteam` trees are the primary tracks offered in baseline's "decide your track" step; `kind: specialization` trees (currently just `leds`) are reached through one or more `parent_trees` instead of picked directly, but still get their own full ladder and poster.
- **`data/tiers.yml`** — the shared 0-4 tier ladder (Baseline/Novice/Journeyman/Expert/Master), used by every tiered tree: `{id, name, verification, supervision?, min_hours_default, requires_taught_tier?}`.
  - `verification` is one of `mentor_signoff` (tiers 0-1), `practical_test` (tier 2), `portfolio_review` (tiers 3-4).
  - `requires_taught_tier` on tiers 3/4 encodes the "senior students must teach" rule: Expert requires having certified someone at Novice, Master requires having certified someone at Journeyman.
- **`data/skills/<tree>.yml`** — one file per tree: `{tree, tier_hours_override?, skills: [{id, tier, name, description?, supervision?, part_of_hybrid?, resources}]}`.
  - `tier_hours_override` lets a tree's actual hour targets differ from `tiers.yml`'s generic defaults (Manufacturing's Novice is 7 hrs, not the generic 25).
  - `resources` is a list of `{type: video|repo|doc, url, path?, label}` — pointers to the actual training material (YouTube videos, the [Skills-Challenges](https://github.com/Raptacon/Skills-Challenges) repo's stepped coding challenges, docs, whatever). Empty `[]` is a valid placeholder until a mentor fills it in.
  - `part_of_hybrid` links a skill to an entry in `hybrids.yml`.
- **`data/hybrids.yml`** — cross-tree hybrid nodes: `{id, name, requires: [{tree, tier}], hours?, skills: [skill_id]}`. A hybrid requires Journeyman (tier 2) in 2+ trees.
- **`data/students/<id>.yml`** — one file per student, stand-in for the future `students`/`verifications`/`checkins` tables: `{name, grad_year, progress: {<tree>: {hours, tier_verified?, skills_completed?, passed? (untiered trees)}}, interests?, hybrids_awarded, badges}`.
  - `skills_completed` is separate from `tier_verified` on purpose: hours and informally-picked-up skills don't themselves grant a tier (see Phase 2's two-gates rule below) — a student can know several skills, or have logged a lot of hours, well before a mentor formally signs off the tier. The one-pager shows both.
  - `interests` is a list of tree ids a student has flagged interest in but hasn't started logging progress against yet — shown as a note, not a gate.

The **LEDs** tree (`data/skills/leds.yml`) is a `kind: specialization` full 0-4 ladder of its own (basic circuits → addressable strips → dot-matrix mapping → an on-robot game with Xbox input) rather than a hybrid, even though it draws on both Electronics and Programming fundamentals — see the comment in `trees.yml` for why it isn't a hybrid, and the "Adding a tree" note below on subteam vs. specialization. Tiers 3-4 describe a learning path only; no dot-matrix hardware or game code exists on the team yet (deliberate scope call, not an oversight).

`generators/common.py` holds the shared YAML-loading helpers (`load_trees`, `load_tiers`, `load_hybrids`, `load_skills`, `tier_hours`, `write_html`) that all three generators build on — add new lookups there rather than re-deriving them per script.

### Adding a tree

1. Add an entry to `data/trees.yml` — `kind: subteam` if it's a primary track new students pick, `kind: specialization` + `parent_trees: [...]` if it's reached through other trees instead (like `leds`).
2. Create `data/skills/<tree>.yml` with at least one skill per tier you want to seed.
3. `make validate`, then `make poster TREE=<tree>`.
4. If it's `kind: subteam`, add it to `baseline-decide-track`'s description in `data/skills/baseline.yml` so new students are actually offered it.

### Adding a skill

Add an entry under the right tree's `skills:` list with a unique `id` (convention: `<tree-prefix>-<short-name>`). `tier` is required; everything else is optional. If it's part of a hybrid, also add/update the matching entry in `hybrids.yml`.

### Adding a hybrid

Add an entry to `data/hybrids.yml` with the two (or more) `{tree, tier}` requirements, then set `part_of_hybrid: <hybrid-id>` on the relevant skill(s) in each tree's skills file.

## The one-pager (`make onepager STUDENT=...`)

Deliberately not a flat report card — it's meant to read as "where you rank and how to level up." Per tiered tree: a rank ladder (Novice/Journeyman/Expert/Master, current rank highlighted), an "Already knows" line for informally-completed skills, and a "Next up" callout with an hours progress bar, the verification method that tier needs, and the specific remaining skills. A **Hybrid opportunities** section surfaces hybrids the student is partway into ("have Programming, still need Journeyman in Electronics") or fully eligible for but not yet awarded ("ready now, ask a mentor").

## The tech-map (`make techmap`)

A single landscape page showing every tree as a lane, tiers 1-4 as columns, the Baseline checklist as a banner strip at the top, and hybrid nodes called out below — meant to answer "how do I get from brand-new to [some goal]?" at a glance, game-tech-tree style. Current version labels each hybrid card with its two parent trees rather than drawing literal connector lines between lanes (lines that actually cross lanes correctly for a graph this connected — e.g. Manufacturing touches Electronics, Design, *and* Programming — need real graph layout, not just CSS grid row-spans). Worth a v2 if the labeled-card version proves too flat in practice.

## Known open items

- **Manufacturing tier overrides**: `mfg-cnc-intro` (tier 1) and `mfg-tool-path-cnc` (tier 3) are read from superscript markers on the mentor's original handwritten draft (`¹`/`³`) as "this skill actually certifies at a different tier than the section it's written under." Flagged with a comment in `data/skills/manufacturing.yml` — confirm with the mentor who wrote the original draft.
- **QR codes** on the poster point at placeholder URLs (`https://raptacon3200.example/skills/<tree>/tier/<n>`) — there's no real resources site yet. Swap `QR_BASE_URL` in `generators/poster.py` once one exists, or point `resources` entries directly at real links per skill.
- **Business/Media tree** (`data/skills/business.yml`) is a from-scratch design (social media, sponsor relations, pit displays, award-submission writing) — sanity-check it against what your business/media subteam actually does.
- **Programming tree's `prog-pid-basics`** doesn't have a real linked resource yet — PID/closed-loop control isn't covered by any current Skills-Challenges step (`challenge_step_4`'s own docs explicitly defer it).
- **LEDs tree tiers 3-4** (dot-matrix mapping, on-robot game) are a designed learning path with no existing hardware/code to link — by design, not an oversight (see the LEDs paragraph above).
- **`elec-mentors-wiring`, `design-owns-cad-standards`** and similar Master-tier "trains others" skills are named explicitly per tree now, but the actual "must have certified someone at tier N" gate still only lives in `tiers.yml`'s `requires_taught_tier` — nothing enforces that the named skill and the gate stay in sync. Not a problem while everything's hand-authored YAML; would need a real check once Phase 2 exists.
- **Hybrid `skills:` lists in `hybrids.yml`** must be kept in sync by hand when a skill's `part_of_hybrid` is added on either parent tree's side (see `dfm`'s list, which now has both a `mfg-*` and a `design-*` id) — easy to forget the other side when adding a new hybrid-tagged skill.

## Phase 2 (not built yet): the full system of record

Design spec for the full system of record:

**Two independent gates per tier (both required):**
1. Hours logged in that tree ≥ the tier's minimum (eligible to *attempt* verification, doesn't itself grant the tier).
2. Verification passed, per `tiers.yml`'s `verification` method for that tier.

**Hours are two kinds:** general presence hours (any check-in, gate Baseline only) vs. in-tree hours (tagged to a specific tree, gate that tree's tiers).

**Privilege gating:** tool access is a hard safety gate on Tier 1-2 in the relevant tree, no override. Subteam lead / board eligibility needs Tier 3 in some tree *plus* a human approval flag — surface "eligible" vs. "approved" separately, never auto-grant leadership.

**Board/Leadership track:** separate competencies (meeting facilitation, budget literacy, sponsor relations, scheduling, conflict resolution, onboarding) tracked as status per competency, not a tier number.

**Commitment badges:** non-gating recognition track, milestones at 25/50/100/250/500 total hours regardless of tree.

**Suggested data model** (Postgres): `students`, `skills(tree, tier, name, description, min_hours, prereq_skill_ids[])`, `verifications(student_id, skill_id, verifier_id, method, date, evidence_url, taught_student_id nullable)`, `hybrid_nodes(name, required_skill_ids[])`, `hybrid_awards`, `checkins(student_id, time_in, time_out, tree_tag nullable, method)`, `board_track`, `badges`. This repo's `data/*.yml` maps directly onto `skills`/`hybrid_nodes`; `data/students/*.yml` maps onto `students`/`verifications`/`checkins` combined.

**Existing infra to integrate with, not replace:**
- QR check-in system already in use — extend it with a check-out step to compute session duration for hours logging.
- RFID / e-paper name tag work in progress separately — future integration point (live tier badges + hour totals on the tag; a tool-station RFID tap logging a "used under supervision" event).
- Shadow spreadsheet (Student, Skill, Tier, Verifier, Date, Hours, Evidence note) is the Phase 1 ledger — a CSV import path is needed so that data isn't lost at go-live.

**Suggested stack:** Go backend + Postgres + REST API; server-rendered templates or htmx over a full JS SPA for the frontend, given the small user base (~20-30 students + mentors).

**Suggested milestone order:** confirm stack → schema/migrations → seed data (import this repo's YAML) → minimal API (record verification, record check-in/out, compute current tier per tree) → read-only team board view (name, tier dots per tree, hybrid stars, hours — the multi-student sibling of this repo's one-pager) → mentor-facing verification forms.
