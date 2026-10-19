#!/usr/bin/env python3
"""Build the whole published site into site/: per-role checklists for every v2
tree, a poster per legacy tiered tree, the techmap, and an index page.
No people data - personal progress comes from the roster, not this site."""

import os
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader

import common

SITE = os.path.join(common.ROOT, "site")
HERE = os.path.dirname(os.path.abspath(__file__))
# Index order: what everyone needs first.
KIND_ORDER = {"onboarding": 0, "core": 1, "certification": 2}


def run(script, *args):
    env = {**os.environ, "OUT": SITE}
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, env=env,
                   stdout=subprocess.DEVNULL)


def main():
    v2 = common.load_v2_trees()
    for tree_id in v2:
        run("checklist.py", tree_id)

    legacy = [t for t in common.load_yaml("trees.yml")["trees"] if t.get("tiered")]
    for t in legacy:
        run("poster.py", t["id"])
    run("techmap.py")

    team = common.load_team()
    os.environ["OUT"] = SITE
    common.OUT = SITE
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.write_html(
        env, "site_index.html.j2", "index.html",
        team=team["team"],
        season=common.current_season(team),
        trees=sorted((d["tree"] for d in v2.values()), key=lambda t: KIND_ORDER.get(t.get("kind"), 99)),
        posters=[{"name": t["name"], "file": f"{t['id']}_poster.html"} for t in legacy],
    )


if __name__ == "__main__":
    main()
