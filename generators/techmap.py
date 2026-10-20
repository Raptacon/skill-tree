#!/usr/bin/env python
"""Render the whole-program tech-tree map: every tree as a lane, tiers as
columns, hybrid nodes called out separately. Driven entirely by content/<team>/*.yml."""

from jinja2 import Environment, FileSystemLoader

import common


def build_context():
    trees = common.load_trees()
    tiers = common.load_tiers()
    hybrids = common.load_hybrids()

    v2 = common.load_v2_trees()
    baseline_skills = [i["name"] for i in common.resolve_items(v2["baseline"], common.own_items(v2))]

    tier_ids = sorted(t for t in tiers if t > 0)

    lanes = []
    for tree in trees.values():
        if not tree.get("tiered", True):
            continue
        skills_doc = common.load_skills(tree["id"])
        skills = skills_doc.get("skills", [])
        columns = []
        for tier_id in tier_ids:
            names = [s["name"] for s in skills if s["tier"] == tier_id]
            columns.append({"tier_name": tiers[tier_id]["name"], "skills": names})
        lanes.append(
            {
                "name": tree["name"],
                "kind": tree.get("kind", "subteam"),
                "parent_trees": [trees[t]["name"] for t in tree.get("parent_trees", []) if t in trees],
                "columns": columns,
            }
        )

    hybrid_cards = []
    for h in hybrids.values():
        parent_names = [trees[r["tree"]]["name"] for r in h["requires"]]
        hybrid_cards.append(
            {
                "name": h["name"],
                "parents": parent_names,
                "hours": h.get("hours"),
            }
        )

    return {
        "tier_names": [tiers[t]["name"] for t in tier_ids],
        "baseline_skills": baseline_skills,
        "lanes": lanes,
        "hybrids": hybrid_cards,
    }


def main():
    env = Environment(loader=FileSystemLoader(common.TEMPLATES))
    common.write_html(env, "techmap.html.j2", "techmap.html", **build_context())


if __name__ == "__main__":
    main()
