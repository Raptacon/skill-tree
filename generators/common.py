"""Shared loading helpers for the generators - keeps content/<team>/*.yml as the
one source of truth without each script re-deriving the same lookups."""

import os
import shutil
from datetime import date

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Team content lives apart from the engine so another team can point CONTENT at
# their own directory without touching generator code.
DATA = os.environ.get("CONTENT", os.path.join(ROOT, "content", "raptacon"))
TMP = os.path.join(ROOT, "tmp")
# Where generated HTML goes. `make site` points this at site/ for publishing.
OUT = os.environ.get("OUT", TMP)
TEMPLATES = os.path.join(ROOT, "generators", "templates")


def load_yaml(name):
    with open(os.path.join(DATA, name)) as f:
        return yaml.safe_load(f)


def load_tiers():
    """{tier_id (int): tier dict}"""
    return {t["id"]: t for t in load_yaml("tiers.yml")["tiers"]}


def load_hybrids():
    """{hybrid_id: hybrid dict}, in file order"""
    return {h["id"]: h for h in load_yaml("hybrids.yml")["hybrids"]}


# --- Trees (trees/*.yml; fields documented in trees/onboarding.yml) ---


def load_v2_trees():
    """{tree_id: full tree doc} for every content/<team>/trees/*.yml"""
    trees_dir = os.path.join(DATA, "trees")
    docs = {}
    for name in sorted(os.listdir(trees_dir)):
        if name.endswith(".yml"):
            doc = load_yaml(os.path.join("trees", name))
            docs[doc["tree"]["id"]] = doc
    return docs


def own_items(trees):
    """{item_id: item} for items defined in some tree (not `{ref: ...}` entries)."""
    return {i["id"]: i for d in trees.values() for i in d["items"] if "ref" not in i}


def resolve_items(tree_doc, items_by_id, include_hidden=False):
    """A tree's items with `{ref: id, section?, tier?}` entries replaced by the
    referenced item (placement overridable), so shared items are defined once
    (docs/adr/0003)."""
    resolved = []
    for item in tree_doc["items"]:
        if "ref" in item:
            target = items_by_id.get(item["ref"])
            if target is None:
                raise SystemExit(f"{tree_doc['tree']['id']}: ref to unknown item '{item['ref']}'")
            item = {**target, **{k: v for k, v in item.items() if k in ("section", "tier")}}
        if include_hidden or item.get("status") != "hidden":
            resolved.append(item)
    return resolved


def load_roles():
    return load_yaml("roles.yml")


def load_team():
    return load_yaml("team.yml")


def current_season(team, today=None):
    """Season label (e.g. '2026-27') for `today`, per team.yml's season.starts."""
    today = today or date.today()
    starts = team["season"]["starts"]
    start_year = today.year if (today.month, today.day) >= (starts["month"], starts["day"]) else today.year - 1
    return team["season"]["label"].format(start_year=start_year, end_year_short=str(start_year + 1)[-2:])


def role_holders(season):
    """{(role_id, tree_id or None): [{name, github}]} for one season of assignments.yml,
    skipping placeholder (TODO) names."""
    holders = {}
    for a in load_yaml("assignments.yml").get("seasons", {}).get(season, []):
        people = [p for p in a.get("holders", []) if p.get("name") and p["name"] != "TODO"]
        holders[(a["role"], a.get("tree"))] = people
    return holders


def item_roles(item):
    """[(role_id, condition_id or None)] - normalizes `roles:` entries."""
    return [(r, None) if isinstance(r, str) else (r["role"], r.get("when")) for r in item.get("roles", [])]


BRAND_ASSETS = ["logo/lockup-horizontal.svg", "logo/raptor-mark.svg"]


def copy_brand_assets():
    """Copy logos from the brand-kit submodule into OUT/assets/."""
    dest = os.path.join(OUT, "assets")
    os.makedirs(dest, exist_ok=True)
    for rel in BRAND_ASSETS:
        src = os.path.join(ROOT, "brand-kit", rel)
        if not os.path.exists(src):
            raise SystemExit(f"Missing {src} - run: git submodule update --init")
        shutil.copy(src, dest)


def write_html(env, template_name, out_name, **context):
    os.makedirs(OUT, exist_ok=True)
    template = env.get_template(template_name)
    html = template.render(**context)
    out_path = os.path.join(OUT, out_name)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Wrote {out_path}")
    return out_path
