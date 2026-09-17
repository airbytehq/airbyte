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

`secrets/` is git-ignored. Credentials only ever come from the configuration: the connector has no
access to AWS profiles, instance roles or environment variables. Two authentication methods:

```json
{
  "credentials": {
    "auth_type": "User",
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "session_token": "only for temporary credentials issued by STS"
  },
  "region": "us-east-1",
  "endpoint": ""
}
```

```json
{
  "credentials": {
    "auth_type": "AssumeRole",
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "role_arn": "arn:aws:iam::123456789012:role/airbyte-dynamodb-reader",
    "external_id": "optional, when the role's trust policy requires one"
  },
  "region": "us-east-1"
}
```

Against a local `amazon/dynamodb-local` container, set `"endpoint": "http://localhost:8000"` and any
non-empty access key id / secret (start the container with `-sharedDb` so the tables are visible
regardless of the access key).

## Relationship with source-dynamodb

`source-dynamodb-v2` keeps the legacy property names (`credentials` with `auth_type: "User"`,
`access_key_id`, `secret_access_key`, `endpoint`, `region`, `reserved_attribute_names`,
`ignore_missing_read_permissions_tables`), so a legacy access-key configuration loads unchanged
(`DynamoDbSourceSpecTest.testLegacyAccessKeyConfigurationStillLoads`). The spec itself deliberately
differs from the legacy one (decision of 2026-09-17: credentials must come from the configuration):

| | source-dynamodb (legacy) | source-dynamodb-v2 |
|---|---|---|
| Role Based Authentication (SDK default credentials chain: env vars, profile, instance role) | yes | removed, no ambient credentials exist in the connector container |
| Access key | `access_key_id`, `secret_access_key` | plus optional `session_token` for temporary STS credentials |
| Access key + `sts:AssumeRole` | no | new `auth_type: "AssumeRole"` with `role_arn` and optional `external_id` (cross-account access) |
| Blank access keys | silently fell back to the default chain | configuration error |
| `region` | optional (`""` allowed), SDK region chain | required, list of the regions known to the pinned AWS SDK (`testRegionEnumMatchesAwsSdk`) |
| `endpoint` | any string | optional, must be an http(s) URL |
| `reserved_attribute_names` | marked `airbyte_secret` | plain string |
| Discovery sample | hard-coded 1000 items per table | `discover_sample_size` (default 1000, 1..100000), like MongoDB's `discover_sample_size` |

AWS has no username/password API authentication; access keys (long-lived or temporary) and role
assumption are the only credential shapes that can travel inside a configuration.

`src/test/resources/legacy-spec.json` is the `spec` output of the published `airbyte/source-dynamodb`
image, kept for reference; `expected-spec.json` is this connector's own snapshot (the strict spec test
writes the current spec to `build/actual-spec.json` to refresh it).

### check and discover parity (verified 2026-09-17 on DynamoDB Local 3.3.1 and on a real AWS account vs 0.3.11)

Against a real account (us-east-2, an IAM user's access key, 4 tables) both images return `SUCCEEDED`
for `check` and byte-identical catalogs for `discover`. With deliberately wrong credentials the new
connector reports: wrong secret -> "The secret access key is invalid ..."; unknown access key id or
bogus session token -> "The access key id or the session token is invalid ..." (AWS uses the same
message for both); a role the key may not assume -> the STS `AccessDenied` message naming the caller
and the role. Legacy returned `FAILED` without a message in all three cases.

- `src/test/resources/expected-catalog.json` is the `CATALOG` object the legacy image produced for the
  seed data in `src/test/resources/parity-seed.json`; `DynamoDbSourceDiscoverTest` seeds a DynamoDB
  Local container with the same data and asserts JSON equality after sorting streams by name.
- Scripts to run both Docker images against one DynamoDB Local container live in the
  `new-database-source-connector` skill (`databases/dynamodb/parity/`).

| Case | Legacy | source-dynamodb-v2 |
|---|---|---|
| `check` failure | `FAILED` with no message (vendor error only in logs) | `FAILED` with a classified message inside "Could not connect with provided configuration. Error: ..." plus an error `TRACE` (`application.yml` regex rules) |
| `check` with zero tables | `SUCCEEDED` | fails with "Discovered zero tables." (`CheckOperation`) |
| `check` without the `credentials` property | NPE message | "Missing required 'credentials' property ..." |
| `discover` of an empty table | stream with `"properties": {}` | stream dropped (`DiscoverOperation` skips streams without fields) |

Everything else in `check` and `discover` is identical, legacy quirks included: `N` values are
`integer` only when they parse as a Java `long`, lists get one `anyOf` entry per element, the last
scanned item wins when an attribute has several types, only the partition (HASH) key is reported as
primary key, and only the first ~1000 scanned items are sampled.
