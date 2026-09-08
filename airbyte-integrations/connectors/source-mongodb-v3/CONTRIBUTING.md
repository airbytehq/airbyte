# Contributing to source-mongodb-v3

`source-mongodb-v3` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core, no toolkits) rewrite of
the legacy `source-mongodb-v2` connector. The legacy connector is the parity oracle: `spec`,
`check`, `discover` and `read` output, saved configurations and persisted state must stay
compatible with it.

## Build and test

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21 2>/dev/null || echo /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home)
./gradlew :airbyte-integrations:connectors:source-mongodb-v3:compileKotlin
./gradlew :airbyte-integrations:connectors:source-mongodb-v3:test          # unit tests (Testcontainers, needs Docker)
./gradlew :airbyte-integrations:connectors:source-mongodb-v3:assemble      # builds airbyte/source-mongodb-v3:dev
```

Unit tests start `mongo:7.0` containers through Testcontainers as a single-node replica set;
change streams and the `check` replica-set probe do not work against a standalone `mongod`.

## Running the connector locally

```bash
docker run --rm airbyte/source-mongodb-v3:dev spec
docker run --rm -v $PWD/secrets:/secrets airbyte/source-mongodb-v3:dev check --config /secrets/config.json
```

`secrets/config.json` is git-ignored. Minimal self-managed example:

```json
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://host1:27017,host2:27017/?replicaSet=rs0",
    "databases": ["my_db"],
    "username": "user",
    "password": "password",
    "auth_source": "admin",
    "schema_enforced": true
  }
}
```

## Parity with source-mongodb-v2

- `src/test/resources/expected-spec.json` is the `spec` output of the published
  `airbyte/source-mongodb-v2` image; `MongoDbSourceSpecTest` fails if the generated spec drifts.
- `MongoDbSpecificationExtender` post-processes the generated JSON schema so that it renders
  exactly like the hand-written legacy `spec.json` (`changelogUrl`, `const` discriminators, no
  `type: object` on `oneOf` variants). Remove it once byte-for-byte parity is no longer required.
- To compare `check` against the legacy image, start an auth-enabled single-node replica set on a
  Docker network (recipe in the `new-database-source-connector` skill, `databases/mongodb/README.md`)
  and run both images on that network with the same `--config` files:

  ```bash
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb-v2:2.0.7 check --config /configs/case.json
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb-v3:dev   check --config /configs/case.json
  ```

  Success output is identical. On failure the Bulk CDK adds an error `TRACE` message and wraps the
  message in "Could not connect with provided configuration. Error: ..."; the wrapped message
  matches the legacy one except for "no authorized collections", where the CDK reports
  "Discovered zero tables.".
