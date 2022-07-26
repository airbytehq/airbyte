docker build . -t airbyte/source-adaptive-insights:dev
docker run --rm airbyte/source-adaptive-insights:dev spec 
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adaptive-insights:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-adaptive-insights:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/sample_files:/sample_files airbyte/source-adaptive-insights:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json

# Download files
# docker cp airbyte-worker:/tmp/airbyte_local/test-adaptive/ .

# Push docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 478610027546.dkr.ecr.us-east-1.amazonaws.com
docker tag airbyte/source-adaptive-insights:dev 478610027546.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-adaptive-insights:dev
docker push 478610027546.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-adaptive-insights:dev