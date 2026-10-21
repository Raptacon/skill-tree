#!/usr/bin/env python3
"""Render a v2 tree (e.g. onboarding) as a printable checklist per role:
what to do, how it gets checked off and who to ask. Driven by
content/<team>/trees/<tree>.yml + roles.yml + assignments.yml + team.yml.

    checklist.py onboarding                 # one page per role (overview.py writes the tree page)
    checklist.py onboarding parent,mentor   # one page for someone holding both roles
"""

import sys

from jinja2 import Environment, FileSystemLoader

import common

RENEWS = {"season": "Every season", "permanent": "Once", "event": "Every trip"}
PRIVATE = {"self": "Private", "mentors": "Mentors only"}


def describe_by(by, ctx):
    """verify.by -> ["Manufacturing Subteam Lead (Sasha Crouse, Snort Hirsch)", ...]"""
    if not by:
        return []
    if "any_of" in by or "all_of" in by:
        return [s for sub in by.get("any_of", by.get("all_of")) for s in describe_by(sub, ctx)]
    if "person" in by:
        return [by["person"]]
    role = ctx["signoff_roles"].get(by["role"])
    if role is None and by["role"] in ctx["member_roles"]:
        return [f"any {ctx['member_roles'][by['role']]['name']}"]   # e.g. {role: mentor}
    label = (role or {"name": by["role"]})["name"]
    if by.get("tree"):
        label = f"{ctx['tree_names'].get(by['tree'], by['tree'])} {label}"
    people = ctx["holders"].get((by["role"], by.get("tree")), [])
    if len(people) > 1:
        label += "s"
    if people:
        label += " (" + ", ".join(p["name"] for p in people) + ")"
    return [label]


def describe_how(item, ctx):
    verify = item.get("verify", {})
    method = verify.get("method")
    who = " or ".join(describe_by(verify.get("by"), ctx))
    if method == "auto":
        text = "Checks itself off from the team roster"
        return text + (f" - questions: {who}" if who else "")
    if method == "self":
        return "Check it off yourself"
    if method == "signature":
        return "Sign the form - checks itself off"
    if item.get("parts") and not who:
        return "Each part is signed off separately - see below"
    if verify.get("claim"):
        return f"Do it, then tell {who} - they confirm it"
    return f"Signed off by {who}"


def describe_target(item):
    kind = item.get("kind")
    if kind == "count":
        return f"{item['target']} needed"
    if kind == "hours":
        return f"{item['target']} hours"
    if kind == "score" and item.get("pass_score") is not None:
        return f"pass score {item['pass_score']}"
    if kind == "timed":
        return f"best of {item.get('runs', 1)} runs - time recorded"
    return None


def describe_requires(item, ctx):
    after = []
    for req in item.get("requires", []):
        if isinstance(req, str):
            after.append(ctx["all_items"].get(req, {"name": req})["name"])
        elif "hours" in req:
            after.append(f"{req['hours']} volunteer hours")
    return after


def applies(item, roles):
    """(applies?, condition ids gating it) for someone holding all of `roles`.
    An item applies if any held role is tagged on it, or the person is its `actor`."""
    always, conditions = False, []
    for role, when in common.item_roles(item):
        if role in roles:
            if when:
                conditions.append(when)
            else:
                always = True
    if item.get("actor") in roles:
        always = True
    return always or bool(conditions), [] if always else conditions


def build_item(item, roles, conditions, ctx):
    actor = item.get("actor")
    tagged = {r for r, _ in common.item_roles(item)}
    actor_note = None
    if actor and actor not in roles:
        actor_note = f"Your {ctx['member_roles'][actor]['name'].lower()} does this one"
    elif actor and actor in roles and not (tagged & set(roles) - {actor}) and tagged - {actor}:
        actor_note = "You do this one for your student"
    return {
        "id": item["id"],
        "track": item.get("track"),
        "mentor_only": item.get("supervision") == "mentor",
        "name": item["name"],
        "description": item.get("description"),
        "conditions": [ctx["conditions"].get(c, {"name": c})["name"] for c in conditions],
        "how": describe_how(item, ctx),
        "target": describe_target(item),
        "renews": RENEWS.get(item.get("renews"), item.get("renews")),
        "private": PRIVATE.get(item.get("visibility")),
        "after": describe_requires(item, ctx),
        "actor_note": actor_note,
        "optional": item.get("required") is False,
        "draft": item.get("status") == "draft",
        "practical": item.get("practical"),
        "training": [r for r in item.get("training", []) if not r.get("roles") or set(r["roles"]) & set(roles)],
        "parts": [{"name": p["name"], "who": " or ".join(describe_by(p.get("by"), ctx))} for p in item.get("parts", [])],
    }


def build_next(tree, ctx):
    nxt = tree.get("next")
    if not nxt:
        return None
    target = nxt.get("tree")
    return {
        "text": nxt.get("text"),
        "link": f"{target}.html" if target in ctx["trees"] else "index.html",
        "label": ctx["tree_names"].get(target, "All skill trees"),
    }


def groups(tree_doc, items):
    """[(name, key, value)]: the tree's sections, or its tiers for tiered trees."""
    if any("tier" in i for i in items):
        tiers = common.load_tiers()
        return [(tiers[t]["name"], "tier", t) for t in sorted(tiers) if t > 0]
    return [(s["name"], "section", s["id"]) for s in tree_doc.get("sections", [])]


def build_context(tree_doc, roles, ctx):
    sections = []
    count = 0
    resolved = common.resolve_items(tree_doc, ctx["all_items"])
    for name, key, value in groups(tree_doc, resolved):
        items = []
        for item in resolved:
            if item.get(key) != value:
                continue
            ok, conditions = applies(item, roles)
            if ok:
                items.append(build_item(item, roles, conditions, ctx))
        if items:
            sections.append({"name": name, "entries": items})
            count += len(items)
    return {
        "tree": tree_doc["tree"],
        "badge": tree_doc["tree"].get("badge"),
        "next": build_next(tree_doc["tree"], ctx),
        "role_names": [ctx["member_roles"][r]["name"] for r in roles],
        "sections": sections,
        "count": count,
        "season": ctx["season"],
        "team": ctx["team"],
    }


def load_ctx():
    trees = common.load_v2_trees()
    roles_doc = common.load_roles()
    team = common.load_team()
    season = common.current_season(team)
    return {
        "trees": trees,
        "tree_names": {s["id"]: s["name"] for s in team.get("subteams", [])}
        | {t["id"]: t["name"] for t in common.load_yaml("trees.yml")["trees"]}
        | {t: d["tree"]["name"] for t, d in trees.items()},
        "all_items": common.own_items(trees),
        "member_roles": {r["id"]: r for r in roles_doc["member_roles"]},
        "signoff_roles": {r["id"]: r for r in roles_doc["signoff_roles"]},
        "conditions": {c["id"]: c for c in roles_doc["conditions"]},
        "holders": common.role_holders(season),
        "season": season,
        "team": team["team"],
    }


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: checklist.py <tree_id> [role[,role...]]")
    tree_id = sys.argv[1]
    ctx = load_ctx()
    if tree_id not in ctx["trees"]:
        raise SystemExit(f"Unknown tree '{tree_id}' - not in trees/")
    tree_doc = ctx["trees"][tree_id]
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)

    if len(sys.argv) == 3:
        roles = sys.argv[2].split(",")
        unknown = [r for r in roles if r not in ctx["member_roles"]]
        if unknown:
            raise SystemExit(f"Unknown role(s): {', '.join(unknown)}")
        common.write_html(env, "checklist.html.j2", f"{tree_id}_{'_'.join(roles)}.html",
                          **build_context(tree_doc, roles, ctx))
        return

    for role in ctx["member_roles"]:
        page = build_context(tree_doc, [role], ctx)
        if page["count"]:
            common.write_html(env, "checklist.html.j2", f"{tree_id}_{role}.html", **page)


if __name__ == "__main__":
    main()
