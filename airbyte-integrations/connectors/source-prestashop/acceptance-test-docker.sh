#!/usr/bin/env sh
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    -w /test_input \
    -e AIRBYTE_SAT_CONNECTOR_DIR=$(pwd) \
    airbyte/source-acceptance-test:dev \
    -p integration_tests.acceptance "$@"
