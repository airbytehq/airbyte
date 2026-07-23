# Local dev and testing commands for source-skillsbase.
#
# Configs (under secrets/ and integration_tests/):
#   - secrets/config.json           real credentials (gitignored)
#   - invalid_config.json           intentionally-bad config
#   - configured_catalog.json       every supported stream
#   - qualifications_catalog.json   smallest stream, for quick sync checks
#
# Authenticated runs pipe through scripts/persist_token.sh, which caches the
# refreshed token in secrets/config.json so the next cold run reuses it instead
# of tripping Skills Base's concurrent-token allowance.

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

CONNECTOR  := source-skillsbase
IMAGE      := airbyte/$(CONNECTOR):dev
BASE_IMAGE := $(shell awk '/baseImage:/ {print $$2; exit}' metadata.yaml)
DOCKERFILE := ../../../docker-images/Dockerfile.manifest-only-connector

DOCKER_RUN := docker run --rm -v "$(CURDIR):/work" $(IMAGE)
CONFIG     := /work/secrets/config.json
INVALID    := /work/integration_tests/invalid_config.json
CATALOG    := /work/integration_tests/configured_catalog.json
QA_CATALOG := /work/integration_tests/qualifications_catalog.json
PEOPLE_CATALOG := /work/integration_tests/people_catalog.json
PERSIST := scripts/persist_token.sh secrets/config.json

.PHONY: help build spec check check-invalid discover read read-qualifications \
        test-acceptance clean unit-test

UNIT_PYTEST := $(shell test -x unit_tests/.venv/bin/pytest && echo "unit_tests/.venv/bin/pytest" || echo "pytest")

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk -F':.*## ' '{printf "  %-22s %s\n", $$1, $$2}'

DOCKER_REPO    := $(shell awk '/dockerRepository:/ {print $$2; exit}' metadata.yaml)
IMAGE_VERSION  := $(shell awk '/dockerImageTag:/ {print $$2; exit}' metadata.yaml)

build:  ## Build the dev Docker image from this connector's manifest.
	docker buildx build --load \
	  -f $(DOCKERFILE) \
	  -t $(IMAGE) \
	  --label io.airbyte.name=$(DOCKER_REPO) \
	  --label io.airbyte.version=$(IMAGE_VERSION) \
	  --build-arg BASE_IMAGE=$(BASE_IMAGE) \
	  --build-arg CONNECTOR_NAME=$(CONNECTOR) \
	  .

spec:  ## Print the connector spec JSON.
	docker run --rm $(IMAGE) spec

gen-spec:  ## Generate integration_tests/spec.json (the expected ConnectorSpecification CAT compares against).
	@docker run --rm $(IMAGE) spec \
	  | jq -c 'select(.type == "SPEC") | .spec' \
	  | jq '.' \
	  > integration_tests/spec.json
	@echo "✅ Wrote integration_tests/spec.json. Re-run after any change to manifest.yaml's spec section."

check:  ## Run check against secrets/config.json (expect succeed). Persists the refreshed token.
	$(DOCKER_RUN) check --config $(CONFIG) | $(PERSIST)

check-invalid:  ## Run check against integration_tests/invalid_config.json (expect fail). No persist.
	$(DOCKER_RUN) check --config $(INVALID)

discover:  ## Discover available streams. Persists the refreshed token.
	$(DOCKER_RUN) discover --config $(CONFIG) | $(PERSIST)

read:  ## Read all streams using configured_catalog.json. Persists the refreshed token.
	$(DOCKER_RUN) read --config $(CONFIG) --catalog $(CATALOG) | $(PERSIST)

read-qualifications:  ## Read only qualifications_assignments (smallest stream, ~15 records on sandbox). Persists the refreshed token.
	$(DOCKER_RUN) read --config $(CONFIG) --catalog $(QA_CATALOG) | $(PERSIST)

read-people:  ## Read only people_assignments (smallest stream, ~15 records on sandbox). Persists the refreshed token.
	$(DOCKER_RUN) read --config $(CONFIG) --catalog $(PEOPLE_CATALOG) | $(PERSIST)

test-acceptance: build  ## Run Connector Acceptance Tests via the official Docker image (rebuilds image and pre-warms token first).
	# Pre-warm the token cache so parallel CAT containers reuse it instead of
	# each hitting /oauth/access_token and tripping the concurrent-token allowance.
	$(DOCKER_RUN) check --config $(CONFIG) | $(PERSIST)
	# Deselect test_backward_compatibility: its fixture docker-pulls
	# $(DOCKER_REPO):latest, which doesn't exist for this Canonical-only connector.
	docker run --rm \
	  -v "$(CURDIR):/test_input" \
	  -v /var/run/docker.sock:/var/run/docker.sock \
	  -e PYTEST_ADDOPTS="-k 'not test_backward_compatibility'" \
	  airbyte/connector-acceptance-test:latest \
	  --acceptance-test-config /test_input

clean:  ## Remove the local dev Docker image.
	-docker rmi $(IMAGE)

unit-test:  ## Run pure-Python unit tests for components.py (no Docker, no Skills Base).
	@if [ ! -x unit_tests/.venv/bin/pytest ]; then \
	  echo "First-time setup: creating unit_tests/.venv and installing deps..."; \
	  python3 -m venv unit_tests/.venv && \
	  unit_tests/.venv/bin/pip install -q --upgrade pip && \
	  unit_tests/.venv/bin/pip install -q -r unit_tests/requirements.txt; \
	fi
	$(UNIT_PYTEST) unit_tests/ -v
