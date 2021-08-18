#!/usr/bin/env sh

UID=$(id -u)
GID=$(id -g)
# Remove container if already exist
echo "Removing previous generator if it exists..."
docker container rm -f airbyte-connector-bootstrap >/dev/null 2>&1

# Build image for container from Dockerfile
# Specify the host system user UID and GID to chown the generated files to host system user.
# This is done because all generated files in container with mounted folders has root owner
echo "Building generator docker image..."
docker build --build-arg UID="$UID" --build-arg GID="$GID" . -t airbyte/connector-bootstrap

# Run the container and mount the airbyte folder
if [ $# -eq 2 ]; then
  echo "2 arguments supplied: 1=$1 2=$2"
  docker run --name airbyte-connector-bootstrap --user $UID:$GID -e package_desc="$1" -e package_name="$2" -v "$(pwd)/../../../.":/airbyte airbyte/connector-bootstrap
else
  echo "Running generator..."
  docker run --rm -it --name airbyte-connector-bootstrap --user $UID:$GID -v "$(pwd)/../../../.":/airbyte airbyte/connector-bootstrap
fi

echo "Finished running generator"

exit 0
