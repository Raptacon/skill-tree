#!/usr/bin/env python
"""Render a single student's progress report: current rank per tree and a
concrete, motivating path to the next one. Driven entirely by data/*.yml."""

import os
import sys

from jinja2 import Environment, FileSystemLoader

import common
import validator


def build_tree_row(tree, tree_id, progress, tiers, top_tier):
    hours = progress.get("hours", 0)
    tier_verified = progress.get("tier_verified", 0)
    skills_doc = common.load_skills(tree_id)
    all_skills = skills_doc.get("skills", [])
    skills_by_id = {s["id"]: s for s in all_skills}
    completed_ids = set(progress.get("skills_completed", []))

    ranks = [
        {
            "tier_id": t,
            "name": tiers[t]["name"],
            "achieved": t <= tier_verified,
            "current": t == tier_verified and t > 0,
        }
        for t in range(1, top_tier + 1)
    ]

    next_tier_id = tier_verified + 1
    next_up = None
    if next_tier_id <= top_tier:
        tier = tiers[next_tier_id]
        target_hours = common.tier_hours(skills_doc, tiers, next_tier_id)
        remaining = [
            s["name"] for s in all_skills if s["tier"] == next_tier_id and s["id"] not in completed_ids
        ]
        next_up = {
            "name": tier["name"],
            "verification": tier["verification"].replace("_", " "),
            "supervision": tier.get("supervision"),
            "requires_taught_tier": tier.get("requires_taught_tier"),
            "hours_target": target_hours,
            "hours_have": hours,
            "hours_pct": min(100, round(100 * hours / target_hours)) if target_hours else None,
            "remaining_skills": remaining,
        }

    known_skills = [skills_by_id[sid]["name"] for sid in completed_ids if sid in skills_by_id]
    try:
        rank_name = tiers[tier_verified]["name"] if tier_verified > 0 else "Not yet ranked"
    except KeyError as e:
        raise SystemExit(f"tier verified: expected a number from 0 to 4; got {e}")

    return {
        "name": tree["name"],
        "tiered": True,
        "hours": hours,
        "rank_name": rank_name,
        "ranks": ranks,
        "next_up": next_up,
        "maxed": next_tier_id > top_tier,
        "known_skills": known_skills,
    }


def hybrid_opportunities(student, trees, hybrids):
    """Hybrids not yet awarded where the student already clears >=1 of the
    two-or-more required trees at Journeyman - the "almost there" nudge."""
    progress = student.get("progress", {})
    awarded = set(student.get("hybrids_awarded", []))
    opportunities = []
    for h in hybrids.values():
        if h["id"] in awarded:
            continue
        met, missing = [], []
        for req in h["requires"]:
            tree_name = trees[req["tree"]]["name"]
            have = progress.get(req["tree"], {}).get("tier_verified", 0)
            (met if have >= req["tier"] else missing).append(tree_name)
        if met and missing:
            opportunities.append({"name": h["name"], "have": met, "missing": missing})
        elif not missing and met:
            opportunities.append({"name": h["name"], "have": met, "missing": [], "ready": True})
    return opportunities


def build_context(student_id):
    path = os.path.join(common.DATA, "students", f"{student_id}.yml")
    if not os.path.exists(path):
        raise SystemExit(f"Unknown student '{student_id}' - no {path}")
    student = common.load_yaml(f"students/{student_id}.yml")

    trees = common.load_trees()
    tiers = common.load_tiers()
    hybrids = common.load_hybrids()
    top_tier = common.max_tier(tiers)

    tree_rows = []
    for tree_id, progress in student.get("progress", {}).items():
        tree = trees.get(tree_id, {"name": tree_id, "tiered": True})
        if not tree.get("tiered", True):
            tree_rows.append(
                {
                    "name": tree["name"],
                    "tiered": False,
                    "passed": progress.get("passed", False),
                    "hours": progress.get("hours", 0),
                }
            )
            continue
        tree_rows.append(build_tree_row(tree, tree_id, progress, tiers, top_tier))

    hybrid_badges = [hybrids[h]["name"] for h in student.get("hybrids_awarded", []) if h in hybrids]
    interest_names = [trees[t]["name"] for t in student.get("interests", []) if t in trees]

    return {
        "name": student["name"],
        "grad_year": student.get("grad_year"),
        "tree_rows": tree_rows,
        "hybrid_badges": hybrid_badges,
        "badges": student.get("badges", []),
        "interests": interest_names,
        "opportunities": hybrid_opportunities(student, trees, hybrids),
    }

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: onepager.py <student_id>")
    student_id = sys.argv[1]
        
    validator.validate_onepager(student_id)
        
    env = Environment(loader=FileSystemLoader(common.TEMPLATES))
    common.write_html(env, "onepager.html.j2", f"{student_id}_onepager.html", **build_context(student_id))


if __name__ == "__main__":
    main()
