docker_image := airbyte/$(notdir $(CURDIR)):dev

run-build:
	docker build . -t ${docker_image}

spec:
	@docker run --rm $(docker_image) spec | jq

check-api-token:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) check --config /secrets/api_token_config.json | jq

check-oauth:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) check --config /secrets/oauth2.0_config.json | jq

discover:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) discover --config /secrets/oauth2.0_config.json | jq

read:
	@docker run --rm -v $(PWD)/secrets:/secrets -v $(PWD)/integration_tests:/integration_tests $(docker_image) read --config /secrets/oauth2.0_config.json --catalog /integration_tests/configured_catalog.json | jq

unittest-local:
	@python -m pytest unit_tests
