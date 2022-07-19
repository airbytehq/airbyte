docker build . -t airbyte/source-adaptive-insights:dev
docker run --rm airbyte/source-adaptive-insights:dev spec 
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adaptive-insights:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adaptive-insights:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/sample_files:/sample_files airbyte/source-adaptive-insights:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json

# Download files
# docker cp airbyte-worker:/tmp/airbyte_local/test-adaptive/ .