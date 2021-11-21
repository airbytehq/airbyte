build:
	cd ../../
	docker build . --build-arg path=destinations/streamr-destination -t mihthanh27/destination-streamr
	cd -

check:
	node bin/main check --config ./airbyte_secret/config.json

spec:
	node bin/main spec

write:
	cat sample_files/records.jsonl | node bin/main write --config airbyte_secret/config.json --catalog sample_files/configured_catalog.json
