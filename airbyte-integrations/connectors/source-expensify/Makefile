# Local dev commands for source-expensify.

POETRY := poetry
SCRIPT := $(POETRY) run source-expensify
CONFIG := --config secrets/config.json
LICENSE_TEMPLATE := ../../../LICENSE_SHORT
LICENSE_SETTINGS := .license-header-settings.json

.PHONY: help install fmt lint test unit-test

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

install:  ## Install project dependencies via Poetry.
	poetry install

fmt:  ## Format source code with ruff and add missing Apache license headers.
	poetry run ruff format .
	poetry run ruff check . --fix
	@missing="$$(grep -rL "Copyright (c)" --include="*.py" .)"; \
	if [ -n "$$missing" ]; then \
		tmpl=$$(mktemp); \
		printf '%s\n' "$$(cat $(LICENSE_TEMPLATE))" > "$$tmpl"; \
		poetry run licenseheaders -f $$missing -t "$$tmpl" -s $(LICENSE_SETTINGS) -o "Airbyte, Inc."; \
		rm -f "$$tmpl"; \
	fi

lint:  ## Lint source code with ruff.
	poetry run ruff check .

unit-test:  ## Run unit tests with pytest.
	poetry run pytest unit_tests

test: lint unit-test  ## Run lint checks and unit tests.

check:
	$(SCRIPT) check $(CONFIG)

discover:
	$(SCRIPT) discover $(CONFIG)

read:
	$(SCRIPT) read $(CONFIG) --catalog integration_tests/configured_catalog.json
