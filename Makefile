##@ Makefile

##@ Define the default airbyte-ci version
AIRBYTE_CI_VERSION ?= 4.48.1

## Detect the operating system
OS := $(shell uname)

tools.airbyte-ci.install: tools.airbyte-ci.clean tools.airbyte-ci-binary.install tools.airbyte-ci.check

tools.airbyte-ci-binary.install: ## Install airbyte-ci binary
	@python airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_install.py ${AIRBYTE_CI_VERSION}

tools.airbyte-ci-dev.install: ## Install the local development version of airbyte-ci
	@python airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_dev_install.py

tools.airbyte-ci.check: ## Check if airbyte-ci is installed correctly
	@./airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_check.sh

tools.airbyte-ci.clean: ## Clean airbyte-ci installations
	@./airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_clean.sh

tools.git-hooks.clean: ## Clean git hooks
	@echo "Unset core.hooksPath"
	@git config --unset core.hooksPath || true
	@echo "Removing pre-commit hooks..."
	@pre-commit uninstall
	@echo "Removing pre-push hooks..."
	@rm -rf .git/hooks
	@echo "Git hooks removed."

tools.pre-commit.install.Linux:
	@echo "Installing pre-commit with pip..."
	@pip install --user pre-commit
	@echo "Pre-commit installation complete."

tools.pre-commit.install.Darwin:
	@echo "Installing pre-commit with brew..."
	@brew install pre-commit
	@echo "Pre-commit installation complete"

tools.git-hooks.install: tools.airbyte-ci.install tools.pre-commit.install.$(OS) tools.git-hooks.clean ## Setup pre-commit hooks
	@echo "Installing pre-commit hooks..."
	@pre-commit install --hook-type pre-push
	@echo "Pre-push hooks installed."

tools.install: tools.airbyte-ci.install tools.pre-commit.install.$(OS)

.PHONY: tools.install tools.pre-commit.install tools.git-hooks.install tools.git-hooks.clean tools.airbyte-ci.install tools.airbyte-ci-dev.install tools.airbyte-ci.check tools.airbyte-ci.clean
