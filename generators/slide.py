#!/usr/bin/env python3
"""Render a 16:9 slide for a tree - for the projector, or to share as a link:
its sections (or tiers) and skills, who signs each off, and QR codes to the
tree's page and, if team.yml sets `signoff_form_url`, the sign-off form.
Written as <tree>_slide.html.

    slide.py <tree_id>
"""

import sys

from jinja2 import Environment, FileSystemLoader

import checklist
import common
import overview


def signers(by, ctx):
    """Names of the people who can sign off, from assignments.yml."""
    if not by:
        return []
    if "any_of" in by or "all_of" in by:
        return [n for sub in by.get("any_of", by.get("all_of")) for n in signers(sub, ctx)]
    return [p["name"] for p in ctx["holders"].get((by.get("role"), by.get("tree")), [])]


def detail_link(item, tree_id):
    """The skill's full details on this tree's checklist (Learn, Test, who signs off)."""
    roles = {r for r, _ in common.item_roles(item)}
    role = next((r for r in ("student", "mentor", "parent", "volunteer", "board") if r in roles), None)
    return f"{tree_id}_{role}.html#{item['id']}" if role else None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: slide.py <tree_id>")
    tree_id = sys.argv[1]
    ctx = checklist.load_ctx()
    ctx["home"] = {i["id"]: tid for tid, d in ctx["trees"].items() for i in d["items"] if "ref" not in i}
    if tree_id not in ctx["trees"]:
        raise SystemExit(f"Unknown tree '{tree_id}'")
    doc = ctx["trees"][tree_id]
    items = common.resolve_items(doc, ctx["all_items"])
    groups = []
    for name, key, value in checklist.groups(doc, items):
        group_items = [i for i in items if i.get(key) == value]
        if group_items:
            people = []
            for i in group_items:
                for person in signers(i.get("verify", {}).get("by"), ctx):
                    if person not in people:
                        people.append(person)
            home = ctx["home"].get(group_items[0]["id"]) if key == "section" else None
            groups.append({
                "name": name,
                "link": f"{home}.html" if home and home != tree_id else None,
                "skills": [{"name": i["name"], "link": detail_link(i, tree_id)} for i in group_items],
                "who": people,
            })

    team = common.load_team()
    site = team["site_url"].rstrip("/")
    tree_url = f"{site}/{tree_id}.html"
    form_url = team.get("signoff_form_url")
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.copy_brand_assets()
    common.write_html(
        env, "slide.html.j2", f"{tree_id}_slide.html",
        tree=doc["tree"], groups=groups, team=team["team"], season=ctx["season"],
        tree_url=tree_url, tree_qr=overview.qr_data_uri(tree_url),
        form_url=form_url, form_qr=overview.qr_data_uri(form_url) if form_url else None,
    )


if __name__ == "__main__":
    main()
