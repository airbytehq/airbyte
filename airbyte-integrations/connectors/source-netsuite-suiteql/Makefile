SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

CONNECTOR := source-netsuite-suiteql
IMAGE ?= airbyte/$(CONNECTOR):dev
IMAGE_TAG ?= dev
CONFIG ?= .secrets/config.json
CATALOG ?= integration_tests/configured_catalog.json
STATE ?= integration_tests/sample_state.json
PYTHON ?= python3
DAGGER ?= dagger
AIRBYTE_CI ?= poetry run airbyte-ci
POETRY ?= poetry
PRE_COMMIT ?= ../../../.venv/bin/pre-commit
SCRIPT := $(POETRY) run $(CONNECTOR)
AIRBYTE_CDK := $(POETRY) run airbyte-cdk

.PHONY: help install build spec check discover read unit-test integration-test connector-test lint test

help:  ## Show available targets and input defaults.
	@printf "Inputs: IMAGE=%s CONFIG=%s CATALOG=%s STATE=%s\n\n" "$(IMAGE)" "$(CONFIG)" "$(CATALOG)" "$(STATE)"
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

install:  ## Install connector dependencies.
	$(POETRY) install

build:  ## Build the development Docker image.
	$(AIRBYTE_CDK) image build --tag $(IMAGE_TAG)

spec:  ## Print the connector specification.
	$(SCRIPT) spec

check:  ## Check credentials from CONFIG.
	$(SCRIPT) check --config $(CONFIG)

discover:  ## Discover streams using CONFIG.
	$(SCRIPT) discover --config $(CONFIG)

read:  ## Read records using CONFIG, CATALOG, and STATE.
	$(SCRIPT) read --config $(CONFIG) --catalog $(CATALOG) --state $(STATE)

unit-test:  ## Run unit tests.
	$(POETRY) run pytest unit_tests

integration-test:  ## Run mocked integration tests.
	$(POETRY) run pytest integration_tests

connector-test:  ## Run connector acceptance configuration validation.
	$(AIRBYTE_CDK) connector test

lint:  ## Run the repository pre-commit checks as in CI
	$(PRE_COMMIT) run --show-diff-on-failure --all-files

test:  ## Run acceptance tests through airbyte-ci.
	cd ../../../airbyte-ci/connectors/pipelines && $(AIRBYTE_CI) connectors --name $(CONNECTOR) test