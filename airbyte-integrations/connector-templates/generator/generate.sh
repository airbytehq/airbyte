#!/usr/bin/env sh
# Remove container if already exist
docker container rm -f airbyte-connector-bootstrap > /dev/null 2>&1
# Stop container if accidentally it is running
docker build . -t airbyte/connector-bootstrap
docker run -it  --name airbyte-connector-bootstrap -v $(pwd)/..:/sources airbyte/connector-bootstrap
docker cp airbyte-connector-bootstrap:/output/. ../../connectors/.
# Remove container after coping files
docker container rm -f airbyte-connector-bootstrap > /dev/null 2>&1
