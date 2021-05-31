#!/usr/bin/env sh
# Remove container if already exist
docker container rm -f airbyte-connector-bootstrap > /dev/null 2>&1
# Build image for container from Dockerfile
docker build . -t airbyte/connector-bootstrap
# Run the container
docker run -it  --name airbyte-connector-bootstrap -v $(pwd)/..:/sources airbyte/connector-bootstrap
# Copy generated template to connectors folder
docker cp airbyte-connector-bootstrap:/connectors/. ../../connectors/.
# Remove container after coping files
docker container rm -f airbyte-connector-bootstrap > /dev/null 2>&1
