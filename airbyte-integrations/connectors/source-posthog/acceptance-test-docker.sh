#!/usr/bin/env bash

# Build latest connector image
docker build . -t "$(grep "connector_image" acceptance-test-config.yml | cut -d: -f2 | xargs)":dev

# Pull latest acctest image
docker pull airbyte/source-acceptance-test:latest

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v "$(pwd):/test_input" \
    airbyte/source-acceptance-test \
    --acceptance-test-config /test_input
