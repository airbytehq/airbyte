## Introduction
MVP for shim over our current entrypoint using `socat`.

Build the `Dockerfile` in the `docker-shim-base`.

Note: This only handle the simpler CDK entrypoint now. This does not handle the more complex
Java entrypoints.

Run as such:
`docker run -it --rm --network=host -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/<built-image>:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json`

Listen on localhost:
`socat -d -d -d TCP-LISTEN:9000,bind=127.0.0.1 stdout`
