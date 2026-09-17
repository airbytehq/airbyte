# Contributing to source-dynamodb-v2

`source-dynamodb-v2` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core, no toolkits) rewrite of the
legacy Java `source-dynamodb` connector. The legacy connector is the parity oracle: `spec`, `check`
and `discover` output and saved configurations must stay compatible with it.

## Build and test

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21 2>/dev/null || echo /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home)
./gradlew :airbyte-integrations:connectors:source-dynamodb-v2:compileKotlin
./gradlew :airbyte-integrations:connectors:source-dynamodb-v2:test      # unit tests (Testcontainers, needs Docker)
./gradlew :airbyte-integrations:connectors:source-dynamodb-v2:assemble  # builds airbyte/source-dynamodb-v2:dev
```

Unit tests start the official `amazon/dynamodb-local` image through Testcontainers, so no AWS
account is needed. DynamoDB Local accepts any access key and does not enforce IAM, which is why the
`ignore_missing_read_permissions_tables` behavior can only be exercised against the real service.

## Running the connector locally

```bash
docker run --rm airbyte/source-dynamodb-v2:dev spec
docker run --rm -v $PWD/secrets:/secrets airbyte/source-dynamodb-v2:dev check --config /secrets/config.json
docker run --rm -v $PWD/secrets:/secrets airbyte/source-dynamodb-v2:dev discover --config /secrets/config.json
```

`secrets/config.json` is git-ignored. Example with an access key:

```json
{
  "credentials": {
    "auth_type": "User",
    "access_key_id": "AKIA...",
    "secret_access_key": "..."
  },
  "region": "us-east-1",
  "endpoint": ""
}
```

Against a local `amazon/dynamodb-local` container, set `"endpoint": "http://localhost:8000"` and any
non-empty access key id / secret (start the container with `-sharedDb` so the tables are visible
regardless of the access key).

## Parity with source-dynamodb

- `src/test/resources/expected-spec.json` is the `spec` output of the published
  `airbyte/source-dynamodb` image; `DynamoDbSourceSpecTest` fails if the generated spec drifts.
- `DynamoDbSpecificationExtender` post-processes the generated JSON schema so that it renders exactly
  like the hand-written legacy `spec.json` (`const` discriminators, no `type: object` on `oneOf`
  variants, root `additionalProperties: false`). Remove it once byte-for-byte parity is no longer
  required.
- `src/test/resources/expected-catalog.json` is the `CATALOG` object the legacy image produced for the
  seed data in `src/test/resources/parity-seed.json`; `DynamoDbSourceDiscoverTest` seeds a DynamoDB
  Local container with the same data and asserts JSON equality after sorting streams by name.
- Scripts to run both Docker images against one DynamoDB Local container live in the
  `new-database-source-connector` skill (`databases/dynamodb/parity/`).

### Known deviations from source-dynamodb (verified 2026-09-17 on DynamoDB Local 3.3.1 vs 0.3.11)

| Case | Legacy | source-dynamodb-v2 |
|---|---|---|
| `check` failure | `FAILED` with no message (vendor error only in logs) | `FAILED` with a classified message inside "Could not connect with provided configuration. Error: ..." plus an error `TRACE` (`application.yml` regex rules) |
| `check` with zero tables | `SUCCEEDED` | fails with "Discovered zero tables." (`CheckOperation`) |
| `check` without the `credentials` property | NPE message | "Missing required 'credentials' property ..." |
| `discover` of an empty table | stream with `"properties": {}` | stream dropped (`DiscoverOperation` skips streams without fields) |

Everything else in `spec`, `check` and `discover` is identical, legacy quirks included: `N` values are
`integer` only when they parse as a Java `long`, lists get one `anyOf` entry per element, the last
scanned item wins when an attribute has several types, only the partition (HASH) key is reported as
primary key, and only the first ~1000 scanned items are sampled.
