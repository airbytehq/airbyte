#!/usr/bin/env bash

error_handler() {
  echo "While trying to generate a connector, an error occurred on line $1 of generate.sh and the process aborted early.  This is probably a bug."
}
trap 'error_handler $LINENO' ERR

set -e

# Ensure script always runs from this directory because thats how docker build contexts work
cd "$(dirname "${0}")" || exit 1

# Make sure docker is running before trying
if ! docker ps; then
  echo "docker is not running, this script requires docker to be up"
  echo "please start up the docker daemon!"
  exit
fi

_UID=$(id -u)
_GID=$(id -g)
# Remove container if already exist
echo "Removing previous generator if it exists..."
docker container rm -f airbyte-connector-bootstrap >/dev/null 2>&1

# Build image for container from Dockerfile
# Specify the host system user UID and GID to chown the generated files to host system user.
# This is done because all generated files in container with mounted folders has root owner
echo "Building generator docker image..."
docker build --build-arg UID="$_UID" --build-arg GID="$_GID" . -t airbyte/connector-bootstrap

# Run the container and mount the airbyte folder
if [ $# -eq 2 ]; then
  echo "2 arguments supplied: 1=$1 2=$2"
  docker run --name airbyte-connector-bootstrap --user "$_UID:$_GID" -e HOME=/tmp -e package_desc="$1" -e package_name="$2" -v "$(pwd)/../../../.":/airbyte airbyte/connector-bootstrap
else
  echo "Running generator..."
  docker run --rm -it --name airbyte-connector-bootstrap --user "$_UID:$_GID" -e HOME=/tmp -v "$(pwd)/../../../.":/airbyte airbyte/connector-bootstrap
fi

echo "Finished running generator"
