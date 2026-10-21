#!/usr/bin/env python3
"""Fail if anything that looks like personal data is in content/ - this repo is
public, so people data belongs in the team roster (Google Sheets), never here.

Flags emails, phone numbers and 8-digit numbers (school IDs). People in YAML are
`{name, github}` only (docs/adr/0004).
"""

import os
import re
import sys

import common

CHECKS = [
    ("email address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("phone number", re.compile(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")),
    ("8-digit ID", re.compile(r"(?<![\d.])\d{8}(?![\d.])")),
]

# Obvious placeholders used by the example student fixtures.
ALLOWED = {"12345678", "87654321"}


def lint_file(path):
    problems = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            for label, pattern in CHECKS:
                for match in pattern.findall(line):
                    if match not in ALLOWED:
                        problems.append(f"{path}:{lineno}: {label} '{match}'")
    return problems


def main():
    problems = []
    for dirpath, _, files in os.walk(common.DATA):
        for name in sorted(files):
            if name.endswith((".yml", ".yaml")):
                problems += lint_file(os.path.join(dirpath, name))
    for p in problems:
        print(p)
    if problems:
        sys.exit(f"{len(problems)} possible personal-data finding(s) - people data goes in the roster, not the repo")
    print("no personal data found")


if __name__ == "__main__":
    main()
