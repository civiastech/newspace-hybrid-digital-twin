.PHONY: install install-dev bootstrap format lint typecheck test smoke quality ci run-db stop-db

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .[dev]

bootstrap:
	bash scripts/bootstrap_env.sh

format:
	black src scripts tests
	ruff check --fix src scripts tests

lint:
	ruff check src scripts tests

typecheck:
	mypy src

test:
	pytest -q

smoke:
	python scripts/run_e2e_smoke.py

quality:
	bash scripts/quality_gate.sh

ci:
	python -m compileall -q src scripts tests
	pytest -q

run-db:
	docker compose -f docker/docker-compose.yml up -d db

stop-db:
	docker compose -f docker/docker-compose.yml down
