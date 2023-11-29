##@ Makefile

##@ Define the default airbyte-ci version
AIRBYTE_CI_VERSION ?= latest

tools.airbyte-ci.install: ## Install airbyte-ci
	@python airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_install.py ${AIRBYTE_CI_VERSION}

tools.airbyte-ci-dev.install: ## Install the development version of airbyte-ci
	@python airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_dev_install.py

tools.airbyte-ci.check: # Check if airbyte-ci is installed correctly
	@./airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_check.sh

tools.airbyte-ci.clean: ## Clean airbyte-ci installations
	@./airbyte-ci/connectors/pipelines/pipelines/external_scripts/airbyte_ci_clean.sh

tools.install: tools.airbyte-ci.install tools.airbyte-ci.check

.PHONY: tools.install tools.airbyte-ci.install tools.airbyte-ci-dev.install tools.airbyte-ci.check tools.airbyte-ci.clean

