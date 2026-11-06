# Contributing to `source-redis`

`source-redis` is a Kotlin Bulk CDK connector. This first version supports
`spec`, `check`, and static `discover`; reading records is not implemented yet.

## Build and test

```bash
./gradlew :airbyte-integrations:connectors:source-redis:compileKotlin
./gradlew :airbyte-integrations:connectors:source-redis:test
./gradlew :airbyte-integrations:connectors:source-redis:spotbugsMain
./gradlew :airbyte-integrations:connectors:source-redis:assemble
```

Tests use Testcontainers and require Docker. They start `redis:8` containers
for command, ACL, TLS, and SSH-tunnel checks.

## Run locally

```bash
docker run --rm airbyte/source-redis:dev spec
docker run -d --name redis -p 6379:6379 redis:8
docker run --rm --network container:redis -v "$PWD/secrets:/secrets:ro" airbyte/source-redis:dev \
  check --config /secrets/config.json
docker run --rm --network container:redis -v "$PWD/secrets:/secrets:ro" airbyte/source-redis:dev \
  discover --config /secrets/config.json
docker rm -f redis
```

For a local Redis configuration, use `localhost` and port `6379`. The
`--network container:redis` option shares Redis's network namespace so
`localhost` reaches the Redis container. Create the configuration file under
a git-ignored `secrets/` directory and do not commit passwords, private keys,
or certificates.

The TLS test certificates are test-only fixtures. Regenerate them with
`src/test/resources/tls/generate-certs.sh`.
