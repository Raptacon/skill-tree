#!/usr/bin/env python3
"""Render path.html: the whole program as one winding trail of stops - Baseline,
then Core Knowledge, then a subteam (picked with tabs). Stops follow each tree's
order (sections, or tiers then file order); trees with `branches` get one trail
per branch, side quests hang off the stop that unlocks them, and drafts show as
locked. Guidance only: no personal progress on this public page."""

import json

from jinja2 import Environment, FileSystemLoader

import checklist
import common
import slide


def stops(doc, items, ctx):
    """[stop] in path order, plus side quests keyed by the stop they hang off."""
    main, side = [], {}
    order = checklist.groups(doc, items)
    for _, key, value in order:
        for i in items:
            if i.get(key) != value:
                continue
            stop = {
                "id": i["id"], "name": i["name"], "description": i.get("description"),
                "tier": i.get("tier"), "branch": i.get("branch"), "draft": i.get("status") == "draft",
                "steps": (i.get("practical") or {}).get("steps") or [],
                "training": [{"label": t.get("label"), "url": t.get("url")} for t in i.get("training") or []],
                "requires": [ctx["all_items"][r]["name"] for r in i.get("requires", []) if r in ctx["all_items"]],
                "signoff": None if i.get("status") == "draft" else common.signoff_link(i, ctx["trees"], ctx["team"]),
                "details": slide.detail_link(i, ctx["home"].get(i["id"], doc["tree"]["id"])),
            }
            if i.get("side_quest"):
                parent = next((r for r in i.get("requires", []) if not ctx["all_items"].get(r, {}).get("side_quest")), None)
                side.setdefault(parent, []).append(stop)
            else:
                main.append(stop)
    return main, side


def world(tree_id, ctx):
    doc = ctx["trees"][tree_id]
    items = common.resolve_items(doc, ctx["all_items"])
    main, side = stops(doc, items, ctx)
    branches = doc["tree"].get("branches") or []
    lanes = []
    if branches:
        for b in branches:
            lanes.append({"name": b["name"], "stops": [s for s in main if s["branch"] == b["id"]]})
        rest = [s for s in main if s["branch"] not in {b["id"] for b in branches}]
        if rest:
            lanes.append({"name": None, "stops": rest, "after": True})
    else:
        lanes.append({"name": None, "stops": main})
    return {"id": tree_id, "name": doc["tree"]["name"], "description": doc["tree"].get("description"),
            "lanes": lanes, "side": side,
            "tiers": doc["tree"].get("kind") == "subteam" and any(s["tier"] for s in main)}


def main():
    ctx = checklist.load_ctx()
    ctx["home"] = {i["id"]: tid for tid, d in ctx["trees"].items() for i in d["items"] if "ref" not in i}
    team = common.load_team()
    ctx["team"] = team
    tiers = {t: d["name"] for t, d in common.load_tiers().items()}
    subteams = sorted((t for t, d in ctx["trees"].items() if d["tree"].get("kind") == "subteam"),
                      key=lambda t: ctx["trees"][t]["tree"]["name"])
    data = {
        "start": [world(t, ctx) for t in ("baseline", "core-knowledge") if t in ctx["trees"]],
        "subteams": [world(t, ctx) for t in subteams],
        "tiers": tiers,
    }
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.copy_brand_assets()
    common.write_html(env, "path.html.j2", "path.html", team=team["team"], season=ctx["season"],
                      data=json.dumps(data).replace("</", "<\\/"))


if __name__ == "__main__":
    main()
