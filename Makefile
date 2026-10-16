NAME = fly_in

PYTHON = python3

MAP = maps/easy/01_linear_path.txt

install:
	$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name 
