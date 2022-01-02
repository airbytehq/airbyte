#!/usr/bin/env sh
image_name="$(grep "connector_image" acceptance-test-config.yml | cut -d: -f2 | xargs)"
# Build latest connector image
echo "try to build: ${image_name}"
docker build . -t "${image_name}"

# Pull latest acctest image
docker pull airbyte/source-acceptance-test:latest

docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v "$(pwd):/test_input" \
    airbyte/source-acceptance-test \
    --acceptance-test-config /test_input
