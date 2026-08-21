SHELL := /bin/bash
PYTHON := pipenv run python

TREE ?= manufacturing
STUDENT ?= example

.PHONY: poster onepager techmap validate clean

poster:
	$(PYTHON) generators/poster.py $(TREE)

onepager:
	$(PYTHON) generators/onepager.py $(STUDENT)

techmap:
	$(PYTHON) generators/techmap.py

validate:
	$(PYTHON) -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('data/**/*.yml', recursive=True)]; print('all yaml valid')"

clean:
	rm -f tmp/*.html tmp/*.png tmp/*.pdf
