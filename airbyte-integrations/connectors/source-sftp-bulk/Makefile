.DEFAULT_GOAL := help
.PHONY: help

help: ## Print this help
	@grep -E '^[0-9a-zA-Z_\-\.]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install using poetry
	@poetry install
	
install.tests: ## Install using poetry using tests extras
	@poetry install -E tests

install.all: ## Install using poetry using all extras
	@poetry install -E tests --with dev


docker.build_dev: ## Build docker development image
	@docker build . -t airbyte/source-sftp-bulk:dev

# ---------------------------------------------------------------------------- #
#                                 test commands                                #
# ---------------------------------------------------------------------------- #


test.unit: ## Run unit tests
	@poetry run pytest unit_tests

test.integration_local: ## Run local integration tests
	@poetry run pytest integration_tests

test.all: ## Run both unit and local integration tests
	@poetry run pytest

test.integration_general: ## Run integration tests
	@poetry run pytest -p connector_acceptance_test.plugin --acceptance-test-config=.

test.clean_containers: ## Clean up stray containers used for integration tests left by vscode. See <https://github.com/microsoft/vscode-python/issues/7055>
	docker container rm -f $$(docker ps --filter name=^pytest.*-mysftp.*$$ -q) || true
	docker network rm $$(docker network ls --filter name=^pytest.*$$ -q) || true