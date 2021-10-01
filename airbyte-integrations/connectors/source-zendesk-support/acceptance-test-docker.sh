#!/usr/bin/env sh
image_name=$(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2-)
# Build latest connector image
echo "try to build: ${image_name}"
docker build . -t ${image_name}

# Pull latest acctest image
docker pull airbyte/source-acceptance-test:latest

docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/source-acceptance-test \
    --acceptance-test-config /test_input
