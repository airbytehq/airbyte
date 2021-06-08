#!/usr/bin/env sh

# Remove container if already exist
docker container rm -f airbyte-connector-bootstrap >/dev/null 2>&1

# Build image for container from Dockerfile
# Specify the host system user UID and GID to chown the generated files to host system user.
# This is done because all generated files in container with mounted folders has root owner
docker build --build-arg UID="$(id -u)" --build-arg GID="$(id -g)" . -t airbyte/connector-bootstrap

# Run the container and mount the airbyte folder
docker run -it --name airbyte-connector-bootstrap -v "$(pwd)/../../../.":/airbyte airbyte/connector-bootstrap

# Remove container after coping files
docker container rm -f airbyte-connector-bootstrap >/dev/null 2>&1

exit 0
