#!/usr/bin/env python
"""Render the whole-program tech map: every tiered tree as a lane, tiers as
columns, Baseline as a banner, hybrids called out separately."""

from jinja2 import Environment, FileSystemLoader

import common

# Subteams first, then specializations, each alphabetical.
LANE_ORDER = {"subteam": 0, "specialization": 1}


def build_context():
    tiers = common.load_tiers()
    hybrids = common.load_hybrids()
    v2 = common.load_v2_trees()
    items = common.own_items(v2)
    names = {t: d["tree"]["name"] for t, d in v2.items()}

    baseline_skills = [i["name"] for i in common.resolve_items(v2["baseline"], items)]
    tier_ids = sorted(t for t in tiers if t > 0)

    lanes = []
    for tree_id, doc in v2.items():
        tree_items = common.resolve_items(doc, items)
        if not any("tier" in i for i in tree_items):
            continue
        tree = doc["tree"]
        lanes.append({
            "id": tree_id,
            "name": tree["name"],
            "kind": tree.get("kind", "subteam"),
            "parent_trees": [names.get(p, p) for p in tree.get("parent_trees", [])],
            "columns": [
                {"tier_name": tiers[t]["name"], "skills": [i["name"] for i in tree_items if i.get("tier") == t]}
                for t in tier_ids
            ],
        })
    lanes.sort(key=lambda lane: (LANE_ORDER.get(lane["kind"], 2), lane["name"]))

    hybrid_cards = [
        {"name": h["name"], "parents": [names.get(r["tree"], r["tree"]) for r in h["requires"]], "hours": h.get("hours")}
        for h in hybrids.values()
    ]

    return {
        "tier_names": [tiers[t]["name"] for t in tier_ids],
        "baseline_skills": baseline_skills,
        "lanes": lanes,
        "hybrids": hybrid_cards,
    }


def main():
    env = Environment(loader=FileSystemLoader(common.TEMPLATES))
    common.copy_brand_assets()
    common.write_html(env, "techmap.html.j2", "techmap.html", **build_context())


if __name__ == "__main__":
    main()
