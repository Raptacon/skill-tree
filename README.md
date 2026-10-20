# Raptacon 3200 Skill Trees

Raptacon 3200's skill trees: what every team member needs to do and learn, from onboarding to subteam mastery. Trees are written in YAML, checked by CI on every pull request, and published as a website and printable checklists.

**Site: https://skills.raptacon.com**

| Tree | For | What it covers |
|---|---|---|
| Onboarding | Students, parents, mentors, volunteers, board | Sign-up, handbook, dues, FIRST registration, safety, getting connected. Renews every season. Finish it: **Rookie**. |
| Baseline | Students, mentors | Hand tools, drills & drivers, git, the team board, how the team works, the robot and game, shadow every subteam, choose a track. Finish it: **Raptor**. |
| Kanban | Students, mentors | GitHub account, how kanban works, using the team board |
| Tool Certifications | Students, mentors | Hands-on sign-off for each shop tool before using it alone |
| Subteam trees | Students | Manufacturing, Design, Electronics, Programming, Business/Media, LEDs - first drafts in the older format, being moved over |

People's progress is **not** in this repo. It lives in the team roster (Google Sheets), run by [raptacon-onboarding-system](https://github.com/Raptacon/raptacon-onboarding-system). This repo only defines the trees.

## Contributing a skill

Mentors and students are encouraged to add and improve skills.

1. Edit or add a tree under `content/raptacon/trees/`. [`onboarding.yml`](content/raptacon/trees/onboarding.yml) documents every field in its header; [`tools.yml`](content/raptacon/trees/tools.yml) is a short example of a hands-on skill.
2. Run `make ci` locally (see Setup) to check it and build the site into `site/`.
3. Open a pull request. CI must pass and a maintainer approves before it merges to `main`; the site updates automatically.

### Item fields

```yaml
- id: tool-drill-driver            # unique across all trees, never changes once in use
  name: Drills & Drivers
  description: What it is and what "done" looks like.
  section: hand-power              # one of the tree's `sections`
  roles: [student, mentor]         # who it applies to; {role: parent, when: chaperone} for conditional
  kind: check                      # check | count | hours | score | signature | external | timed
  requires: [onb-safety-test]      # items (any tree) or {hours: N} that must come first
  verify:
    method: signoff                # auto | self | signoff | signature | score
    by: {role: subteam-lead, tree: manufacturing}   # roles from roles.yml
  training:                        # how to learn it
    - {type: session, label: Walkthrough with a co-lead}
    - {type: video, label: Drill basics, url: "https://..."}
  practical:                       # the test: the exact hands-on task, in order
    summary: Done in front of a co-lead.
    steps: [Get the drill from its spot., ...]
  renews: season                   # season | permanent | event
  visibility: public               # public | team | mentors | self
```

- `parts: [{id, name, by}]` splits an item into named sign-offs (Baseline's "Shadow every subteam" has one per subteam).
- A tree can set `badge: {name, description}` (the rank for finishing it) and `next: {tree, text}` (where to go after).

- A tree can reuse another tree's item with `{ref: <item-id>}`; completing it once counts in both.
- Trees and items carry `authored_by: [{name, github}]`, `created_at` and `updated_at`.
- **No personal data in this repo.** People appear only as `{name, github}`. CI fails on emails, phone numbers and 8-digit IDs.

### Other content files

| File | Holds |
|---|---|
| `content/raptacon/roles.yml` | Member roles (student, parent, mentor, volunteer, board), conditions (chaperone, CCSD volunteer, ...), sign-off roles |
| `content/raptacon/assignments.yml` | Who holds each sign-off role this season, so checklists say who to ask |
| `content/raptacon/team.yml` | Team name/number and when the season rolls over |
| `content/raptacon/trees.yml`, `tiers.yml`, `hybrids.yml`, `skills/` | Older-format subteam trees (tier 0-4 ladders), still rendered as posters |

## Setup

```bash
git submodule update --init               # brand-kit (logo); or clone with --recurse-submodules
pipenv install
make ci                                   # validate YAML, lint for personal data, build site/
make overview TREE=programming            # a tree's main page: tiers as rows, skills as cards
make checklist TREE=onboarding            # per-role checklists + index into tmp/
make checklist TREE=onboarding ROLES=parent,mentor   # one page for someone with both roles
make poster TREE=manufacturing            # older-format tree poster
make techmap                              # every older-format tree on one page
```

Open the generated HTML in a browser to view or print it.

Another team can point the generators at its own content with `CONTENT=/path/to/content make ci`.

## Design

Decisions and their reasons are in [`docs/adr/`](docs/adr/README.md): one onboarding file with role-tagged items, Google Sheets as the progress store, a shared item library with trees as views, per-item verification/renewal/visibility, and a public repo with no personal data.

## License

[MIT](LICENSE)
