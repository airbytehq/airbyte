#!/usr/bin/env sh

# Build latest connector image
docker build . -t $(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2-)

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/source-acceptance-test:dev \
    --acceptance-test-config /test_input

