#!/usr/bin/env python3
"""Write catalog.json: every item, tree, role and this season's sign-off
assignments in one machine-readable file. The progress system in
raptacon-onboarding-system reads it to build the sign-off form and to check
that a sign-off came from someone allowed to give it (docs/adr/0002, 0006).
Published at <site_url>/catalog.json. Names and GitHub usernames only."""

import json
import os
import subprocess
from datetime import datetime, timezone

import common

ITEM_FIELDS = ["name", "description", "kind", "target", "runs", "pass_score", "actor", "verify", "parts",
               "requires", "renews", "visibility", "supervision", "status", "tier", "section", "track"]


def commit():
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=common.ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build():
    trees = common.load_v2_trees()
    roles = common.load_roles()
    team = common.load_team()
    season = common.current_season(team)
    own = common.own_items(trees)

    homes = {i["id"]: tid for tid, d in trees.items() for i in d["items"] if "ref" not in i}
    appears = {}
    for tid, doc in trees.items():
        for item in common.resolve_items(doc, own, include_hidden=True):
            appears.setdefault(item["id"], []).append(tid)

    items = {}
    for item_id, item in own.items():
        entry = {k: item[k] for k in ITEM_FIELDS if k in item}
        entry["home_tree"] = homes[item_id]
        entry["trees"] = appears.get(item_id, [homes[item_id]])
        entry["roles"] = [{"role": r, "when": w} if w else {"role": r} for r, w in common.item_roles(item)]
        items[item_id] = entry

    assignments = common.load_yaml("assignments.yml").get("seasons", {}).get(season, [])

    return {
        "schema": 1,
        "team": team["team"],
        "season": season,
        "commit": commit(),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "trees": [
            {k: d["tree"][k] for k in ("id", "name", "kind", "parent_trees", "requires", "badge") if k in d["tree"]}
            for d in trees.values()
        ],
        "tiers": [{k: t[k] for k in t} for t in common.load_yaml("tiers.yml")["tiers"]],
        "items": items,
        "member_roles": [r["id"] for r in roles["member_roles"]],
        "conditions": [c["id"] for c in roles["conditions"]],
        "signoff_roles": [{k: r[k] for k in ("id", "name", "scoped") if k in r} for r in roles["signoff_roles"]],
        "assignments": [
            {"role": a["role"], **({"tree": a["tree"]} if a.get("tree") else {}),
             "people": [p for p in a.get("holders", []) if p.get("name") != "TODO"]}
            for a in assignments
        ],
    }


def main():
    os.makedirs(common.OUT, exist_ok=True)
    path = os.path.join(common.OUT, "catalog.json")
    with open(path, "w") as f:
        json.dump(build(), f, indent=1, default=str)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
