##@ Makefile

##@ Define the default version
VERSION ?= latest

tools.airbyte-ci.install: ## Install airbyte-ci
	@./tools/bin/make/airbyte_ci_install.sh ${VERSION}

tools.airbyte-ci-dev.install: ## Install the development version of airbyte-ci
	@./tools/bin/make/airbyte_ci_dev_install.sh

tools.airbyte-ci.check: # Check if airbyte-ci is installed correctly
	@./tools/bin/make/airbyte_ci_check.sh

tools.airbyte-ci.clean: ## Clean airbyte-ci installations
	@./tools/bin/make/airbyte_ci_clean.sh

tools.install: tools.airbyte-ci.install tools.airbyte-ci.check

.PHONY: tools.install tools.airbyte-ci.install tools.airbyte-ci-dev.install tools.airbyte-ci.check tools.airbyte-ci.clean

