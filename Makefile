SHELL := /bin/bash
PYTHON := pipenv run python

TREE ?= manufacturing
STUDENT ?= example

.PHONY: poster onepager techmap checklist validate clean

poster:
	$(PYTHON) generators/poster.py $(TREE)

onepager:
	$(PYTHON) generators/onepager.py $(STUDENT)

techmap:
	$(PYTHON) generators/techmap.py

# One printable checklist per role + an index page, e.g. make checklist TREE=onboarding
# ROLES=parent,mentor renders a single combined page for someone holding several roles.
checklist:
	$(PYTHON) generators/checklist.py $(TREE) $(ROLES)

validate:
	$(PYTHON) -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('content/**/*.yml', recursive=True)]; print('all yaml valid')"

clean:
	rm -f tmp/*.html tmp/*.png tmp/*.pdf
