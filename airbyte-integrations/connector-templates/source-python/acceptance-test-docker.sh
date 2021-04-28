#!/usr/bin/env sh
docker run --rm -i airbyte/source-acceptance-test \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v ./:/test_input \
    -w /test_input \
    -p integration_tests.acceptance
