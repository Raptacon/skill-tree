# ADR-0007: Skills are a DAG; skill-sets are views over it

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** Chris Hirsch

## Context
Every skill already has a global id (ADR-0003), and `requires` links skills across trees. Together they form a graph: 193 skills and 165 prerequisite edges as of this ADR, with no cycles. Trees (Programming, Baseline…) are one way to view that graph, but the team keeps asking for others:

- a goal like "Vision Programmer" or "Drive Coach", gathered from several trees
- team roles from the handbook (pit crew, lead scout, technician) as clear requirements
- fun collections ("every skill that starts with C") with their own badge
- working backwards: "what does Jane still need to become a Vision Programmer, in what order?"

## Decision

### 1. Skills are nodes in one directed acyclic graph (DAG)
- `requires` edges point from a skill to its prerequisites. **Cycles are invalid**; CI rejects them.
- `requires` entries may be:
  - an item id, meaning that skill is required
  - `{any_of: [a, b]}`, meaning either one will do
  - `{hours: N}`, a threshold

```yaml
- id: leds-strip-control
  requires:
    - leds-strip-power
    - any_of: [elec-crimping, prog-libraries-docs]   # come in from Electronics or Programming
```

- Skills may carry `tags` for meaning that cuts across trees, and `est_hours` for planning:

```yaml
- id: prog-vision
  tags: [vision, controls]
  est_hours: 12
```

### 2. Skill-sets are named views: by list, or by rule
Skill-sets live in `content/<team>/skill_sets/*.yml`. A set either lists skills or selects them with a small rule. Arbitrary code is never allowed in a rule.

**By list**, a goal:
```yaml
id: vision-programmer
name: Vision Programmer
description: Get cameras finding targets and driving the robot to them.
skills: [prog-vision, prog-pid, prog-swerve, prog-subsystems, elec-can-bus]
badge: {name: Vision Programmer}
badge_holds: while-current      # or: forever
```

**By rule**, using tags:
```yaml
id: pit-crew
name: Pit Crew
description: Everything you need to work the pit at competition.
match: {tags_any: [pit-crew]}
badge: {name: Pit Crew}
badge_holds: while-current
```

**By rule**, just for fun:
```yaml
id: c-collector
name: The C Collector
description: Every skill whose name starts with C. Because why not.
match: {name_prefix: "C"}
badge: {name: C Collector}
badge_holds: forever
```

**A team role**, from handbook section 7.2:
```yaml
id: drive-coach
name: Drive Coach (eligible to try out)
skills: [strat-robot-cone-course, strat-game-rules-test, strat-match-strategist]
role: drive-coach               # links to the roster Roles tab (ADR-0006)
badge_holds: while-current
```

A `match` rule may use only: `tags_any`, `tags_all`, `trees`, `tier_max`, `tier_min`, `kind`, `name_prefix`, `ids`. These are combined with AND.

### 3. Prerequisites are pulled in automatically
For any skill-set, the generator computes:
- **Everything needed:** the set plus all of its prerequisites. For `any_of`, it takes the branch with fewer prerequisites, and shows the other as an alternative.
- **The order:** a topological sort, so nothing comes before its prerequisites, then by tier, then by tree.
- **The estimated effort:** the sum of `est_hours` where it's known.

The site publishes one **path page** per skill-set: everything needed, in order, with the Learn / Test / who-signs-off detail for each skill.

### 4. Progress uses the same graph
In the progress system (ADR-0002), given what a person has done:
- **Unlocked next:** skills whose prerequisites are all complete. This is "what can I do next?"
- **Closest:** for each skill-set, what's left and how much effort it is. For the team, "who's closest to Drive Coach?"
- **Badges:**
  - `forever` badges are earned once.
  - `while-current` badges show as active only while every skill in the set is current for the season.

### 5. Trees stay as they are
A tree is a curated view with tiers or sections and a rank badge. Skill-sets don't replace trees; they're another view of the same nodes. `catalog.json` gains `skill_sets[]` so the progress system can evaluate them.

## Consequences
- New goals, roles and badges are YAML-only changes. Nothing else needs to change.
- Ids and edges must stay stable and acyclic. The validator (issue #1) checks cycles, references and `match` rules.
- `any_of` makes "everything needed" a choice, not one fixed set. Path pages show the chosen route and the alternative.
- `badge_holds: while-current` adds a little work to the progress system, but keeps safety-related sets honest.

## Not decided yet
- Whether students can define their own personal skill-sets (goals) in the progress system, or only mentors via PR.
- Graph visualization (nodes and arrows): Tech Map v2.

Trees remain curated, directed paths set by a mentor or lead; skill-sets add views on top of them.
