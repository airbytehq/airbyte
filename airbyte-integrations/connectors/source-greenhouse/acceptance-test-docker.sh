#!/usr/bin/env sh

set -e

CDK_DIR=../../../airbyte-cdk

if [ -n "$USE_LOCAL_CDK" ]; then
  # Build the Docker images associated with the local version of the CDK
  docker build -f $CDK_DIR/Dockerfile.connectors $CDK_DIR --build-arg USE_LOCAL_CDK=$USE_LOCAL_CDK -t airbyte/airbyte-cdk-connectors
  docker build -f $CDK_DIR/Dockerfile.sats $CDK_DIR --build-arg USE_LOCAL_CDK=$USE_LOCAL_CDK -t airbyte/airbyte-cdk-sats
  # Build the SAT Docker image
  docker build ../../bases/source-acceptance-test --build-arg USE_LOCAL_CDK=$USE_LOCAL_CDK -t airbyte/source-acceptance-test
else
  # Pull latest acctest image
  docker pull airbyte/connector-acceptance-test:latest
fi

# Build latest connector image
docker build . --build-arg USE_LOCAL_CDK=$USE_LOCAL_CDK -t $(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2)

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/connector-acceptance-test \
    --acceptance-test-config /test_input

