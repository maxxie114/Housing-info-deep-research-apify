#!/bin/bash
set -a
source .env
set +a
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
