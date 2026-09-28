.PHONY: install lint test quality

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check flaky_investigator tests

test:
	pytest

quality: lint test
