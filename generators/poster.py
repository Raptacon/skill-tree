#!/usr/bin/env python
"""Render a tree's skill poster as HTML, driven entirely by data/*.yml."""

import base64
import io
import sys

import qrcode
from jinja2 import Environment, FileSystemLoader

import common

# Placeholder landing-page base until mentors have a real resources site.
QR_BASE_URL = "https://raptacon3200.example/skills"


def qr_data_uri(url):
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_context(tree_id):
    trees = common.load_trees()
    tiers = common.load_tiers()
    hybrids = common.load_hybrids()
    skills_doc = common.load_skills(tree_id)

    if tree_id not in trees:
        raise SystemExit(f"Unknown tree '{tree_id}' - not in data/trees.yml")

    tree = trees[tree_id]
    skills = skills_doc.get("skills", [])

    skills_by_id = {s["id"]: s for s in skills}
    hybrids_by_tree = [h for h in hybrids.values() if any(r["tree"] == tree_id for r in h["requires"])]

    # Attach the hybrid's display name onto any skill that belongs to it.
    for s in skills:
        if s.get("part_of_hybrid"):
            s["hybrid_name"] = hybrids[s["part_of_hybrid"]]["name"]

    tier_rows = []
    for tier_id in sorted(tiers):
        tier_skills = [s for s in skills if s["tier"] == tier_id]
        if not tier_skills:
            continue
        tier = tiers[tier_id]
        hours = common.tier_hours(skills_doc, tiers, tier_id)
        qr_url = f"{QR_BASE_URL}/{tree_id}/tier/{tier_id}"
        tier_rows.append(
            {
                "id": tier_id,
                "name": tier["name"],
                "verification": tier["verification"].replace("_", " "),
                "supervision": tier.get("supervision"),
                "hours": hours,
                "requires_taught_tier": tier.get("requires_taught_tier"),
                "skills": tier_skills,
                "qr": qr_data_uri(qr_url),
                "qr_url": qr_url,
            }
        )

    hybrid_cards = []
    for h in hybrids_by_tree:
        other_trees = [r["tree"] for r in h["requires"] if r["tree"] != tree_id]
        hybrid_cards.append(
            {
                "name": h["name"],
                "other_trees": [trees.get(t, {"name": t})["name"] for t in other_trees],
                "hours": h.get("hours"),
                "skills": [skills_by_id[sid]["name"] for sid in h.get("skills", []) if sid in skills_by_id],
            }
        )

    return {
        "tree_name": tree["name"],
        "kind": tree.get("kind", "subteam"),
        "tier_rows": tier_rows,
        "hybrids": hybrid_cards,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: poster.py <tree_id>")
    tree_id = sys.argv[1]

    env = Environment(loader=FileSystemLoader(common.TEMPLATES))
    common.write_html(env, "poster.html.j2", f"{tree_id}_poster.html", **build_context(tree_id))


if __name__ == "__main__":
    main()
