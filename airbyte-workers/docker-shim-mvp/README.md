## Introduction
MVP for shim over our current entrypoint using `socat`.

1. From the `~/code/airbyte` directory run `./gradlew :airbyte-integrations:connectors:source-always-works:airbyteDocker`

2. From `~/code/airbyte/airbyte-integrations/connectors/source-always-works/docker-shim-mvp/docker-shim-base` run `docker build -t airbyte/docker-shim-base:dev .`

Note: This only handle the simpler CDK entrypoint now. This does not handle the more complex
Java entrypoints.

3. Run `echo "{\"limit\": 1000}" >  ~/code/airbyte/airbyte-integrations/connectors/source-always-works/secrets/config.json`

4. Listen on localhost:
   `socat -d -d -d TCP-LISTEN:9000,bind=127.0.0.1 stdout`

5. From `~/code/airbyte/airbyte-integrations/connectors/source-always-works`, run `docker run -it --rm --network=host -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests -e SRC_IP=host.docker.internal -e SRC_PORT=9000 airbyte/docker-shim-base:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json`
