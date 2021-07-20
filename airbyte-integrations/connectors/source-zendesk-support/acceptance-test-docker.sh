#!/usr/bin/env sh
 ./discover2catalog.sh main.py  ./secrets/config.json  ./integration_tests/configured_catalog.json
docker build . -t airbyte/source-zendesk-support:dev

docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/source-acceptance-test \
    --acceptance-test-config /test_input
