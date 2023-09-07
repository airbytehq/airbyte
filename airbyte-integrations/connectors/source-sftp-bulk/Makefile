.DEFAULT_GOAL := help
.PHONY: help

help: ## Print this help
	@grep -E '^[0-9a-zA-Z_\-\.]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install using poetry
	@poetry install
	
install.all: ## Install using poetry using all extras
	@poetry install --all-extras

# ---------------------------------------------------------------------------- #
#                                 test commands                                #
# ---------------------------------------------------------------------------- #

test: ## Run tests
	@poetry run pytest

test.unit: ## Run unit tests
	@poetry run pytest unit_tests

test.integration: install.all ## Run integration tests
	@poetry run pytest -p connector_acceptance_test.plugin --acceptance-test-config=.