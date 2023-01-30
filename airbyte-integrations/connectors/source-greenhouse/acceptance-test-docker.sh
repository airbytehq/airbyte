#!/usr/bin/env sh

set -e

ROOT_DIR=../../..
SITE_PACKAGES_LOCATION=/usr/local/lib/python3.9/site-packages/
CONNECTOR_TAG=$(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2)
CONNECTOR_NAME=$(echo $CONNECTOR_TAG | cut -d / -f 2)
VOLUME_NAME=$CONNECTOR_NAME-local-cdk

# Build latest connector image
docker build . -t $CONNECTOR_TAG:dev

if [ -n "$LOCAL_CDK" ]; then
  # Build an image with the Python environment of the connector, built against the local CDK
  docker build -f $ROOT_DIR/Dockerfile.local_cdk -t airbyte/$VOLUME_NAME --build-arg CONNECTOR_NAME=$CONNECTOR_NAME $ROOT_DIR
  # Create the volume, seeded with the installed Python environment for the connector
  docker volume rm $VOLUME_NAME 2>/dev/null || true
  docker run --mount source=$VOLUME_NAME,destination=$SITE_PACKAGES_LOCATION airbyte/$VOLUME_NAME
  # Build the SAT Docker image; TODO: remove this once the SAT image has been updated
  docker build ../../bases/source-acceptance-test -t airbyte/source-acceptance-test
else
  # Pull latest acctest image
  docker pull airbyte/connector-acceptance-test:latest
fi

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    -e LOCAL_CDK=$LOCAL_CDK \
    -e VOLUME_NAME=$VOLUME_NAME \
    airbyte/connector-acceptance-test \
    --acceptance-test-config /test_input

