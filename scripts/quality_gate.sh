#!/usr/bin/env bash
set -euo pipefail
python -m compileall -q src scripts tests
ruff check src scripts tests
black --check src scripts tests
pytest -q
