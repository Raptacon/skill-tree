#!/usr/bin/env python3
"""Publish Bibbidi-Bobbidi-Bash (the bash-game submodule) at <OUT>/bash/ with
Raptacon's module config (content/<team>/bash-game.yaml). Mirrors the game's
own `make build` assembly: copy the sources, embed the config as a script so it
also works from disk, and version the asset URLs for cache-busting."""

import glob
import json
import os
import re
import shutil

import common

GAME = os.path.join(common.ROOT, "bash-game")


def main():
    if not os.path.exists(os.path.join(GAME, "index.html")):
        raise SystemExit(f"Missing {GAME} - run: git submodule update --init")
    dest = os.path.join(common.OUT, "bash")
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(os.path.join(dest, "css"))
    os.makedirs(os.path.join(dest, "js"))

    shutil.copy(os.path.join(GAME, "index.html"), dest)
    shutil.copy(os.path.join(GAME, "css", "style.css"), os.path.join(dest, "css"))
    for path in sorted(glob.glob(os.path.join(GAME, "js", "*.js"))):
        shutil.copy(path, os.path.join(dest, "js"))
    shutil.copy(os.path.join(GAME, "VERSION"), dest)

    with open(os.path.join(common.DATA, "bash-game.yaml")) as f:
        config = f.read()
    with open(os.path.join(dest, "config.yaml"), "w") as f:
        f.write(config)
    with open(os.path.join(dest, "js", "config-embed.js"), "w") as f:
        f.write(f"window.BBB_CONFIG_YAML = {json.dumps(config)};\n")

    with open(os.path.join(GAME, "VERSION")) as f:
        version = f.read().strip()
    index = os.path.join(dest, "index.html")
    with open(index) as f:
        html = f.read()
    tag = '<script src="js/config.js"></script>'
    if tag not in html:
        raise SystemExit("bash-game index.html no longer loads js/config.js - update generators/bashgame.py")
    html = html.replace(tag, '<script src="js/config-embed.js"></script>\n  ' + tag)
    html = re.sub(r'(src|href)="((?:js|css)/[^"?]+)"', lambda m: f'{m.group(1)}="{m.group(2)}?v={version}"', html)
    with open(index, "w") as f:
        f.write(html)
    print(f"Wrote {dest}/ (Bibbidi-Bobbidi-Bash {version})")


if __name__ == "__main__":
    main()
