SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

CONNECTOR := source-kapa
IMAGE ?= airbyte/$(CONNECTOR):dev
CONFIG ?= .secrets/config.json
CATALOG ?= integration_tests/configured_catalog.json
STATE ?= integration_tests/sample_state.json
PYTHON ?= python3
DAGGER ?= dagger
AIRBYTE_CI ?= poetry run airbyte-ci
AIRBYTE_CDK ?= airbyte-cdk
UV ?= uv

BASE_IMAGE := $(shell awk '/baseImage:/ {print $$2; exit}' metadata.yaml)
DOCKER_REPOSITORY := $(shell awk '/dockerRepository:/ {print $$2; exit}' metadata.yaml)
IMAGE_VERSION := $(shell awk '/dockerImageTag:/ {print $$2; exit}' metadata.yaml)
DOCKERFILE := ../../../docker-images/Dockerfile.manifest-only-connector

.PHONY: help build spec check discover read unit-test connector-test test

help:  ## Show available targets and input defaults.
	@printf "Inputs: CONFIG=%s CATALOG=%s STATE=%s\n\n" "$(CONFIG)" "$(CATALOG)" "$(STATE)"
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

build:  ## Build the manifest-only development image.
	docker buildx build --load \
		-f $(DOCKERFILE) \
		-t $(IMAGE) \
		--label io.airbyte.name=$(DOCKER_REPOSITORY) \
		--label io.airbyte.version=$(IMAGE_VERSION) \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		--build-arg CONNECTOR_NAME=$(CONNECTOR) \
		.

spec: build  ## Build the image and print the connector specification.
	docker run --rm $(IMAGE) spec

check: build  ## Check credentials from CONFIG.
	docker run --rm -v "$(CURDIR)/$(CONFIG):/config.json:ro" $(IMAGE) check --config /config.json

discover: build  ## Discover streams using CONFIG.
	docker run --rm -v "$(CURDIR)/$(CONFIG):/config.json:ro" $(IMAGE) discover --config /config.json

read: build  ## Run an incremental read using CONFIG, CATALOG, and STATE.
	docker run --rm \
		-v "$(CURDIR)/$(CONFIG):/config.json:ro" \
		-v "$(CURDIR)/$(CATALOG):/catalog.json:ro" \
		-v "$(CURDIR)/$(STATE):/state.json:ro" \
		$(IMAGE) read --config /config.json --catalog /catalog.json --state /state.json

unit-test:  ## Run manifest runtime tests in an isolated CDK environment.
	$(UV) run --isolated --python $(PYTHON) \
		--with 'airbyte-cdk==7.21.1' \
		--with 'pytest>=8,<9' \
		--with 'pytest-mock>=3.14,<4' \
		--with 'requests-mock>=1.12,<2' \
		pytest unit_tests -q

connector-test:  ## Run credential-free CDK standard tests and configured bypasses.
	$(AIRBYTE_CDK) connector test $(CURDIR)

test:  ## Run connector acceptance through airbyte-ci (requires its Poetry environment).
	cd ../../../airbyte-ci/connectors/pipelines && $(AIRBYTE_CI) connectors --name $(CONNECTOR) test
