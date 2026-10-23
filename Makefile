SHELL := /bin/bash
PYTHON := pipenv run python

TREE ?= manufacturing

.PHONY: techmap checklist overview validate lint site ci clean

techmap:
	$(PYTHON) generators/techmap.py

# One printable checklist per role, e.g. make checklist TREE=onboarding
# ROLES=parent,mentor renders a single combined page for someone holding several roles.
checklist:
	$(PYTHON) generators/checklist.py $(TREE) $(ROLES)

# A tree's main page: tiers/sections as rows, skills as expandable cards, QR per row
overview:
	$(PYTHON) generators/overview.py $(TREE)

validate:
	$(PYTHON) generators/validator.py

lint:
	$(PYTHON) generators/lint.py

# Everything the published site needs, into site/
site:
	rm -rf site
	$(PYTHON) generators/site.py

# What CI runs on every PR
ci: validate lint site

clean:
	rm -f tmp/*.html tmp/*.png tmp/*.pdf
