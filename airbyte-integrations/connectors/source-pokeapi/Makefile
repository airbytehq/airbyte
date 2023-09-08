DOCKER_REPOSITORY = $(shell cat metadata.yaml | grep 'dockerRepository' | cut -d : -f 2 | tr -d '[[:blank:]]')
PROJECT_TOP_LEVEL = $(shell git rev-parse --show-toplevel)

all: check

format-ruff:
	poetry run ruff --fix .

format-black:
	poetry run black .

lint-black:
	poetry run black . --check

lint-ruff:
	poetry run ruff .

lint-mypy:
	poetry run mypy src tests || true

build-python:
	rm -rf dist build/dist
	mkdir -p build
	poetry build
	mv dist build/

build-docker:
	docker build . -t $(DOCKER_REPOSITORY):dev

format: format-ruff format-black

lint: lint-mypy lint-ruff lint-black

test:
	poetry run pytest

integration_test:
	source "$(PROJECT_TOP_LEVEL)/airbyte-integrations/bases/connector-acceptance-test/acceptance-test-docker.sh"

build: build-python build-docker

check: lint test
