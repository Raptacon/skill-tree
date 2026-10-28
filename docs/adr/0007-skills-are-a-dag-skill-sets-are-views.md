# ADR-0007: Skills are a DAG; skill-sets are views over it

- **Status:** Accepted
- **Date:** 2026-10-22 (revised 2026-10-23 after review by Rayl Morris)
- **Deciders:** Chris Hirsch

## Context
Every skill already has a global id (ADR-0003), and `requires` links skills across trees. Together they form a graph: 193 skills and 165 prerequisite edges as of this ADR, with no cycles. Trees (Programming, Baseline…) are one way to view that graph, but the team keeps asking for others:

- a goal like "Vision Programmer" or "Drive Coach", gathered from several trees
- team roles from the handbook (pit crew, lead scout, technician) as clear requirements
- fun collections ("every skill that starts with C") with their own badge
- working backwards: "what does Jane still need to become a Vision Programmer, in what order?"

Rayl Morris's review shaped three parts of this decision: a single selector for skill-sets, keeping thresholds out of the graph, and how tags relate to skills.

## Decision

### 1. Skills are nodes in one directed acyclic graph (DAG)
A **skill** is anything that can be tested and signed off. Each skill is a node; `requires` describes what must come first. **Cycles are invalid**; CI rejects them.

### 2. `requires`: edges vs. conditions
Authors write one `requires` list, but its entries are of two different kinds:

**Edges** - part of the DAG, used for cycle checks and path planning:
- an item id - that skill is required
- `{any_of: [a, b]}` - either one will do. For cycle checks it counts as an edge to every alternative; for path planning it's a choice.
- `{tree: X}` - every skill in tree X. It expands to edges to those skills.

**Conditions** - not part of the DAG; checked against the person when progress is evaluated:
- `{hours: N}` (optionally `{hours: N, tree: X}`) - logged hours, overall or in one tree

```yaml
- id: leds-strip-control
  requires:
    - leds-strip-power                                  # edge
    - any_of: [elec-crimping, prog-libraries-docs]      # edge (either)
- id: onb-ccsd-fingerprinting
  requires:
    - onb-ccsd-volunteer-forms                          # edge
    - hours: 150                                        # condition
```

Thresholds are **not** modelled as virtual nodes. Nobody signs off "60 hours" - it's a fact about a person that changes continuously - and a virtual node would show up in "unlocked next" and distort path ordering.

### 3. Skills, tags and skill-sets are different things
| If it… | It's a… | Example |
|---|---|---|
| can be **tested and signed off** | **skill** (node) | *Vision system integration* - a capstone that requires `prog-vision` and has its own test |
| is a **grouping** with nothing to test as a whole | **tag** | `vision` on prog-vision, camera mounting, lighting |
| groups skills **and earns something** | **skill-set** | *Vision Programmer*: skills tagged `vision` + a badge |

- **Never create a skill just to group other skills.** It would need someone to sign it off, appear in "unlocked next", and duplicate a tag plus a skill-set.
- **Tags never create edges.** They are metadata for selecting skills.
- Tags come from a controlled vocabulary in `content/<team>/tags.yml`; the validator rejects unknown tags so `vision`, `Vision` and `vison` can't all appear.

```yaml
- id: prog-vision
  tags: [vision, controls]
  est_hours: 12            # optional, for planning
```

### 4. Skill-sets are named views, chosen with one `match` selector
Skill-sets live in `content/<team>/skill_sets/*.yml`. Each one picks its skills with a single `match` selector - there's no separate "list" form, because a list is just a selector:

- A **clause** is a set of filters combined with **AND**. Filters: `skills` (an explicit list of ids), `tags_any`, `tags_all`, `trees`, `tier_min`, `tier_max`, `kind`, `name_prefix`.
- `any_of: [clause, …]` takes the **union** of clauses - this is how lists and rules combine.
- `exclude: [ids]` removes skills at the end.
- Arbitrary code is never allowed.

**A goal - an explicit list:**
```yaml
id: vision-programmer
name: Vision Programmer
description: Get cameras finding targets and driving the robot to them.
match:
  skills: [prog-vision, prog-pid, prog-swerve, prog-subsystems, elec-can-bus]
badge: {name: Vision Programmer}
badge_holds: while-current      # or: forever
```

**A role - a list plus a rule:**
```yaml
id: pit-crew
name: Pit Crew
description: Everything you need to work the pit at competition.
match:
  any_of:
    - skills: [strat-robot-knowledge, elec-battery-safety]
    - tags_any: [pit-crew]
  exclude: [mfg-runs-shop]
role: pit-crew                  # links to the roster Roles tab (ADR-0006)
badge: {name: Pit Crew}
badge_holds: while-current
```

**A team role from handbook section 7.2:**
```yaml
id: drive-coach
name: Drive Coach (eligible to try out)
match:
  skills: [strat-robot-cone-course, strat-game-rules-test, strat-match-strategist]
role: drive-coach
badge_holds: while-current
```

**Just for fun - a rule:**
```yaml
id: c-collector
name: The C Collector
description: Every skill whose name starts with C. Because why not.
match: {name_prefix: "C"}
badge: {name: C Collector}
badge_holds: forever
```

### 5. Prerequisites are pulled in automatically
For any skill-set, the generator computes:
- **Everything needed:** the selected skills plus all of their prerequisite edges (transitively). For `any_of`, it takes the branch with fewer prerequisites and shows the other as an alternative. Conditions (hours) are listed alongside.
- **The order:** a topological sort - nothing before its prerequisites - then by tier, then by tree.
- **The estimated effort:** the sum of `est_hours` where known.

The site publishes one **path page** per skill-set: everything needed, in order, with Learn / Test / who-signs-off for each skill.

### 6. Progress uses the same graph
In the progress system (ADR-0002), given what a person has done:
- **Unlocked next:** skills whose prerequisite edges are all complete and whose conditions are met - "what can I do next?"
- **Closest:** for each skill-set, what's left and how much effort - and for the team, "who's closest to Drive Coach?"
- **Badges:** `forever` badges are earned once; `while-current` badges are active only while every skill in the set is current for the season.

### 7. Trees stay as they are
A tree is a curated, directed path set by a mentor or lead, with tiers or sections and a rank badge. Skill-sets don't replace trees; they're another view of the same nodes. `catalog.json` gains `skill_sets[]` and `tags[]` so the progress system can evaluate them.

## Consequences
- New goals, roles and badges are YAML-only changes.
- Ids and edges must stay stable and acyclic. The validator (issue #1) checks cycles, references, tags against `tags.yml`, and `match` selectors.
- One selector means one evaluator and one validator path, and lists and rules combine freely.
- `any_of` makes "everything needed" a choice; path pages show the chosen route and the alternative.
- `badge_holds: while-current` adds a little work to the progress system, but keeps safety-related sets honest.

## Not decided yet
- Whether students can define their own personal skill-sets (goals) in the progress system, or only mentors via PR.
- Graph visualization (nodes and arrows): Tech Map v2.
