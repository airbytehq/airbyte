docker_image := airbyte/$(notdir $(CURDIR)):dev

run-build:
	docker build . -t ${docker_image}

spec:
	@docker run --rm $(docker_image) spec | jq

check-valid:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) check --config /secrets/config.json | jq

check-invalid:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) check --config /secrets/invalid_config.json | jq

discover:
	@docker run --rm -v $(PWD)/secrets:/secrets $(docker_image) discover --config /secrets/config.json | jq

read:
	@docker run --rm -v $(PWD)/secrets:/secrets -v $(PWD)/sample_files:/sample_files $(docker_image) read --config /secrets/config.json --catalog /sample_files/configured_catalog.json | jq

read-incremental:
	@docker run --rm -v $(PWD)/secrets:/secrets -v $(PWD)/sample_files:/sample_files $(docker_image) read --config /secrets/config.json --catalog /sample_files/configured_catalog_incremental.json --state /sample_files/state.json | jq

read-incremental-abnormal:
	@docker run --rm -v $(PWD)/secrets:/secrets -v $(PWD)/sample_files:/sample_files $(docker_image) read --config /secrets/config.json --catalog /sample_files/configured_catalog_incremental.json --state /sample_files/abnormal_state.json | jq
