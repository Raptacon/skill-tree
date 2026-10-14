"""Shared loading helpers for the generators - keeps content/<team>/*.yml as the
one source of truth without each script re-deriving the same lookups."""

import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Team content lives apart from the engine so another team can point CONTENT at
# their own directory without touching generator code.
DATA = os.environ.get("CONTENT", os.path.join(ROOT, "content", "raptacon"))
TMP = os.path.join(ROOT, "tmp")
TEMPLATES = os.path.join(ROOT, "generators", "templates")


def load_yaml(name):
    with open(os.path.join(DATA, name)) as f:
        return yaml.safe_load(f)


def load_trees():
    """{tree_id: tree dict}"""
    return {t["id"]: t for t in load_yaml("trees.yml")["trees"]}


def load_tiers():
    """{tier_id (int): tier dict}"""
    return {t["id"]: t for t in load_yaml("tiers.yml")["tiers"]}


def load_hybrids():
    """{hybrid_id: hybrid dict}, in file order"""
    return {h["id"]: h for h in load_yaml("hybrids.yml")["hybrids"]}


def load_skills(tree_id):
    """Full skills doc for one tree: {tree, tier_hours_override?, skills: [...]}"""
    return load_yaml(os.path.join("skills", f"{tree_id}.yml"))


def max_tier(tiers):
    return max(t for t in tiers if t > 0)


def tier_hours(skills_doc, tiers, tier_id):
    """A tree's actual hour target for a tier, honoring tier_hours_override."""
    override = skills_doc.get("tier_hours_override", {})
    return override.get(tier_id, tiers[tier_id].get("min_hours_default"))


def write_html(env, template_name, out_name, **context):
    os.makedirs(TMP, exist_ok=True)
    template = env.get_template(template_name)
    html = template.render(**context)
    out_path = os.path.join(TMP, out_name)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Wrote {out_path}")
    return out_path
