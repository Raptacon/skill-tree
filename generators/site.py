#!/usr/bin/env python3
"""Build the whole published site into site/: an overview page and per-role
checklists for every tree, the techmap, catalog.json and an index.
No people data - personal progress comes from the roster, not this site."""

import os
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader

import common

SITE = os.path.join(common.ROOT, "site")
HERE = os.path.dirname(os.path.abspath(__file__))
# Index order: what everyone needs first.
# Trees that get a 16:9 slide (<tree>_slide.html) for meetings and join nights.
SLIDES = ["onboarding", "baseline", "core-knowledge"]
KIND_ORDER = {"onboarding": 0, "baseline": 1, "core-knowledge": 2, "core": 3, "certification": 4}


def run(script, *args):
    env = {**os.environ, "OUT": SITE}
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, env=env,
                   stdout=subprocess.DEVNULL)


def main():
    v2 = common.load_v2_trees()
    for tree_id in v2:
        run("checklist.py", tree_id)
    for tree_id in v2:
        run("overview.py", tree_id)
    run("techmap.py")
    for tree_id in SLIDES:
        run("slide.py", tree_id)
    run("catalog.py")

    team = common.load_team()
    common.OUT = SITE
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.write_html(
        env, "site_index.html.j2", "index.html",
        team=team["team"],
        season=common.current_season(team),
        trees=sorted((d["tree"] for d in v2.values() if d["tree"].get("kind") in KIND_ORDER),
                     key=lambda t: KIND_ORDER[t["kind"]]),
        specializations=sorted([d["tree"] for d in v2.values() if d["tree"].get("kind") == "specialization"],
                               key=lambda t: t["name"]),
        subteams=sorted([d["tree"] for d in v2.values() if d["tree"].get("kind") == "subteam"],
                        key=lambda t: t["name"]),
    )


if __name__ == "__main__":
    main()
