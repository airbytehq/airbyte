#!/bin/bash
# Tag a connector dev image as custom for a given connector and add proxy settings.
# With that file, the image for the connector will have proxy settings defined.

# Usage: ./build_custom_docker_image.sh <connector-name>

CONNECTOR=$1

echo "🚀 Setting up custom docker image for manifest-only connector $CONNECTOR..."

CUSTOM_IMAGE="airbyte/$CONNECTOR:custom"
DEV_IMAGE="airbyte/$CONNECTOR:dev"

docker build \
  --build-arg BASE_IMAGE=$DEV_IMAGE \
  -t "$CUSTOM_IMAGE" \
  - <<EOF
FROM $DEV_IMAGE
ENV HTTP_PROXY=${IMAGE_HTTP_PROXY}
ENV HTTPS_PROXY=${IMAGE_HTTPS_PROXY}
EOF

echo "✅ Custom image built for connector $CONNECTOR"
