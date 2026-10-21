#!/usr/bin/env python3
"""Build the whole published site into site/: an overview page per tree (v2
and older-format), per-role checklists for v2 trees, the techmap and an index.
No people data - personal progress comes from the roster, not this site."""

import os
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader

import common

SITE = os.path.join(common.ROOT, "site")
HERE = os.path.dirname(os.path.abspath(__file__))
# Index order: what everyone needs first.
KIND_ORDER = {"onboarding": 0, "baseline": 1, "core": 2, "certification": 3}


def run(script, *args):
    env = {**os.environ, "OUT": SITE}
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, env=env,
                   stdout=subprocess.DEVNULL)


def main():
    v2 = common.load_v2_trees()
    legacy = [t for t in common.load_yaml("trees.yml")["trees"] if t.get("tiered")]
    for tree_id in v2:
        run("checklist.py", tree_id)
    for tree_id in [*v2, *(t["id"] for t in legacy)]:
        run("overview.py", tree_id)
    run("techmap.py")

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
        subteams=sorted([{"id": d["tree"]["id"], "name": d["tree"]["name"], "draft": False}
                         for d in v2.values() if d["tree"].get("kind") not in KIND_ORDER
                         and d["tree"].get("kind") != "specialization"]
                        + [{"id": t["id"], "name": t["name"], "draft": True} for t in legacy],
                        key=lambda t: t["name"]),
    )


if __name__ == "__main__":
    main()
