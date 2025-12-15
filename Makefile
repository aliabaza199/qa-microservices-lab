SHELL := /bin/bash

SERVICE_DIR := services/sample-api
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "Targets:"
	@echo "  make venv       Create local virtualenv"
	@echo "  make install    Install deps for sample-api (editable + test deps)"
	@echo "  make test       Run pytest for sample-api"
	@echo "  make up         Start services with docker compose"
	@echo "  make down       Stop services"
	@echo "  make logs       Tail docker logs"
	@echo "  make health     Call GET /health"
	@echo "  make clean      Remove venv + pytest cache"
	@echo ""

.PHONY: venv
venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PY) -m pip install --upgrade pip

.PHONY: install
install: venv
	@$(PIP) install -e ./$(SERVICE_DIR)[test]

.PHONY: test
test: install
	@$(VENV)/bin/pytest -q $(SERVICE_DIR)/tests

.PHONY: up
up:
	docker compose up --build

.PHONY: down
down:
	docker compose down

.PHONY: logs
logs:
	docker compose logs -f --tail=200

.PHONY: health
health:
	@curl -s http://localhost:8000/health | python3 -m json.tool

.PHONY: clean
clean:
	rm -rf $(VENV) .pytest_cache
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \; 2>/dev/null || true
