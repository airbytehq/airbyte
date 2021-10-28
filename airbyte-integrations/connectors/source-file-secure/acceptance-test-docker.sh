#!/usr/bin/env sh

# Build latest connector image
source_image=$(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2-)
echo "try to build the source image: ${source_image}"
docker build  -t ${source_image} .

# Pull latest acctest image
docker pull airbyte/source-acceptance-test:latest

docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/source-acceptance-test \
    --acceptance-test-config /test_input
