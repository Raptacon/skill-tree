#!/usr/bin/env python3
"""Render a tree's overview page: one row per tier (or per section, for trees
without tiers), each skill a card that expands in place, a QR code per row back
to the site. Works for v2 trees (trees/*.yml) and older-format trees
(trees.yml + skills/*.yml). Written as <tree>.html - each tree's main page.

    overview.py <tree_id>
"""

import base64
import io
import sys

import qrcode
from jinja2 import Environment, FileSystemLoader

import common

ROLE_ORDER = ["student", "mentor", "parent", "volunteer", "board"]


def qr_data_uri(url):
    img = qrcode.make(url, border=1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def tier_meta(tier, hours):
    return {
        "supervision": tier.get("supervision"),
        "hours": hours,
        "verification": tier["verification"].replace("_", " "),
        "taught": tier.get("requires_taught_tier"),
    }


def row(row_id, name, tree_id, ctx, cards, meta=None):
    url = f"{ctx['site_url']}/{tree_id}.html#{row_id}"
    return {"id": row_id, "name": name, "cards": cards, "meta": meta, "qr": qr_data_uri(url), "qr_url": url}


def v2_card(item, tree_id, home, ctx):
    roles = [r for r in ROLE_ORDER if r in {role for role, _ in common.item_roles(item)}]
    detail = f"{tree_id}_{roles[0]}.html#{item['id']}" if roles else None
    origin = home.get(item["id"])
    return {
        "name": item["name"],
        "description": item.get("description"),
        "test": bool(item.get("practical")),
        "timed": item.get("runs", 1) if item.get("kind") == "timed" else None,
        "track": item.get("track"),
        "parts": len(item.get("parts", [])),
        "mentor_only": item.get("supervision") == "mentor",
        "renews": item.get("renews") == "season",
        "shared": ctx["tree_names"].get(origin) if origin and origin != tree_id else None,
        "draft": item.get("status") == "draft",
        "detail": detail,
        "bonus": item.get("bonus", []),
    }


def tree_hybrids(tree_id, ctx):
    return [
        {"name": h["name"], "with": [ctx["tree_names"].get(r["tree"], r["tree"]) for r in h["requires"] if r["tree"] != tree_id],
         "projects": h.get("projects", [])}
        for h in common.load_hybrids().values()
        if any(r["tree"] == tree_id for r in h["requires"])
    ]


def build_v2(tree_id, ctx):
    doc = ctx["trees"][tree_id]
    items = common.resolve_items(doc, ctx["all_items"])
    home = ctx["home"]
    tiers = common.load_tiers()
    rows = []
    if any("tier" in i for i in items):
        overrides = doc["tree"].get("tier_hours", {})
        for tier_id in sorted(t for t in tiers if t > 0):
            cards = [v2_card(i, tree_id, home, ctx) for i in items if i.get("tier") == tier_id]
            if cards:
                tier = tiers[tier_id]
                hours = overrides.get(tier_id, tier.get("min_hours_default"))
                rows.append(row(tier["name"].lower(), tier["name"], tree_id, ctx, cards, tier_meta(tier, hours)))
    else:
        for section in doc.get("sections", []):
            cards = [v2_card(i, tree_id, home, ctx) for i in items if i.get("section") == section["id"]]
            if cards:
                rows.append(row(section["id"], section["name"], tree_id, ctx, cards))
    roles = sorted({r for i in items for r, _ in common.item_roles(i)}, key=ROLE_ORDER.index)
    tree = doc["tree"]
    starts = [f"{ctx['all_items'][r]['name']} ({ctx['tree_names'].get(home.get(r), home.get(r))})"
              for r in tree.get("requires", []) if r in ctx["all_items"]]
    return {
        "name": tree["name"],
        "starts_after": starts,
        "description": tree.get("description"),
        "badge": tree.get("badge"),
        "next": tree.get("next"),
        "checklists": [{"role": ctx["member_roles"][r]["name"], "file": f"{tree_id}_{r}.html"} for r in roles],
        "rows": rows,
        "hybrids": tree_hybrids(tree_id, ctx),
        "specializations": [
            {"id": t, "name": d["tree"]["name"],
             "with": [ctx["tree_names"].get(p, p) for p in d["tree"].get("parent_trees", []) if p != tree_id]}
            for t, d in ctx["trees"].items()
            if d["tree"].get("kind") == "specialization" and tree_id in d["tree"].get("parent_trees", [])
        ],
        "reached_from": [ctx["tree_names"].get(p, p) for p in tree.get("parent_trees", [])],
        "draft": False,
    }


def build_legacy(tree_id, ctx):
    tree = ctx["legacy"][tree_id]
    skills_doc = common.load_skills(tree_id)
    tiers = common.load_tiers()
    rows = []
    for tier_id in sorted(t for t in tiers if t > 0):
        skills = [s for s in skills_doc.get("skills", []) if s["tier"] == tier_id]
        if skills:
            tier = tiers[tier_id]
            cards = [{"name": s["name"], "description": s.get("description")} for s in skills]
            meta = tier_meta(tier, common.tier_hours(skills_doc, tiers, tier_id))
            rows.append(row(tier["name"].lower(), tier["name"], tree_id, ctx, cards, meta))
    hybrids = tree_hybrids(tree_id, ctx)
    return {
        "name": tree["name"],
        "description": None,
        "badge": None,
        "next": None,
        "checklists": [],
        "rows": rows,
        "hybrids": hybrids,
        "draft": True,
    }


def load_ctx():
    trees = common.load_v2_trees()
    legacy = {t["id"]: t for t in common.load_yaml("trees.yml")["trees"]}
    team = common.load_team()
    home = {i["id"]: tid for tid, d in trees.items() for i in d["items"] if "ref" not in i}
    return {
        "trees": trees,
        "legacy": legacy,
        "home": home,
        "all_items": common.own_items(trees),
        "member_roles": {r["id"]: r for r in common.load_roles()["member_roles"]},
        "tree_names": {s["id"]: s["name"] for s in team.get("subteams", [])}
        | {t: d["name"] for t, d in legacy.items()}
        | {t: d["tree"]["name"] for t, d in trees.items()},
        "site_url": team["site_url"].rstrip("/"),
        "team": team["team"],
        "season": common.current_season(team),
    }


def render(tree_id, ctx, env):
    if tree_id in ctx["trees"]:
        page = build_v2(tree_id, ctx)
    elif tree_id in ctx["legacy"]:
        page = build_legacy(tree_id, ctx)
    else:
        raise SystemExit(f"Unknown tree '{tree_id}'")
    if page.get("next") and page["next"].get("tree"):
        page["next"]["link"] = f"{page['next']['tree']}.html"
        page["next"]["label"] = ctx["tree_names"].get(page["next"]["tree"], page["next"]["tree"])
    return common.write_html(env, "overview.html.j2", f"{tree_id}.html",
                             page=page, team=ctx["team"], season=ctx["season"])


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: overview.py <tree_id>")
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.copy_brand_assets()
    render(sys.argv[1], load_ctx(), env)


if __name__ == "__main__":
    main()
