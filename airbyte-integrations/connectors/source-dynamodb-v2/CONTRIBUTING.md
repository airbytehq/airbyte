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

## How `read` works

Every configured table is one stream feed with one partition (tables are read concurrently with
each other up to the `concurrency` setting, default 1; a single table is never split into parallel
`Segment` scans in this version, see the concurrency note in the PR). The partition reader issues `Scan` requests page
by page (`ExclusiveStartKey` = the previous page's `LastEvaluatedKey`), projecting exactly the
attributes of the configured stream. Every attribute is referenced through a placeholder
(`#a0, #a1, ...` in `ExpressionAttributeNames`), so reserved words and special characters need no
configuration (`reserved_attribute_names` is kept for backward compatibility and ignored).

Items are converted to JSON like the legacy `DynamodbAttributeSerializer`: `S` string, `N` number
(a `long` when it fits, otherwise the exact decimal), `B` base64 string, sets and lists as arrays,
`M` as an object, `BOOL`, `NULL`. Attributes an item does not have are emitted as `null`.

The stream state (`stream_state`) is backward compatible with the legacy `DbStreamState`:

| Situation | `stream_state` |
|---|---|
| Incremental scan complete (also what the legacy connector emitted) | `{"cursor_field":["updated_at"],"cursor":"2024-05-01T10:00:00Z","cursor_record_count":1}` |
| Scan in progress (checkpoint after a page; `checkpoint_target_interval_seconds`, default 300) | the fields above (the lower bound the scan filters on) plus `"scan":{"exclusive_start_key":{"pk":{"S":"..."}},"max_cursor":"...","max_cursor_record_count":1}` |
| Full refresh in progress | `{"scan":{"exclusive_start_key":{...}}}` |
| Full refresh complete (legacy emitted no state for full refresh) | `{"scan_complete":true}` |

Incremental sync keeps the legacy semantics: the cursor is a top-level `S` or `N` attribute, the
scan filters on `cursor > :saved` (`>=` when the saved value is a bare date such as `2016-02-15`),
the whole table is still scanned and billed, the highest cursor value seen becomes the next cursor
once the scan is complete, and a changed cursor attribute starts over. A legacy state (with its
`stream_name`/`stream_namespace` and the `data` duplicate) is read as is, so existing connections
resume without a reset. An `exclusive_start_key` is written in DynamoDB JSON and typed by the
table's key schema (`S`, `N`, `B`).

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
| Checkpoints | none (one state at the end of an incremental stream) | `checkpoint_target_interval_seconds` (default 300) like the JDBC Bulk sources: a state after every round of scan pages, resumable full refresh |
| Concurrency | tables read one after another | `concurrency` (optional, default 1, like the JDBC Bulk sources): maximum number of tables scanned at the same time |

AWS has no username/password API authentication; access keys (long-lived or temporary) and role
assumption are the only credential shapes that can travel inside a configuration.

`src/test/resources/legacy-spec.json` is the `spec` output of the published `airbyte/source-dynamodb`
image, kept for reference; `expected-spec.json` is this connector's own snapshot (the strict spec test
writes the current spec to `build/actual-spec.json` to refresh it). CI's format check runs prettier
3.0.3 on every JSON and YAML file; after refreshing a snapshot (or `parity-seed.json`,
`expected-catalog.json`) reformat it, for example without a local node:

```bash
docker run --rm -v "$PWD":/work -w /work node:20-alpine sh -c \
  'npm i -g --silent prettier@3.0.3 && prettier --write src/test/resources/*.json'
```

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

### read parity (verified 2026-09-17 on DynamoDB Local 3.3.1 and on a real AWS account vs 0.3.11)

Against the real account (us-east-2, 4 tables, 6 items) both images return byte-identical records
for a full refresh of every table (strict comparison, no normalization needed), identical records
and identical final states (`cursor`, `cursor_record_count`) for incremental syncs on two string
cursors, and a state handoff works in both directions: the new connector resumed from the legacy
state messages and the legacy connector from the new one, each with zero new records. Legacy could
only read those tables with `reserved_attribute_names` listing every attribute: a name starting
with `_` (`_airbyte_data`) is a `ValidationException: Invalid ProjectionExpression: Syntax error;
token: "_"` for it, and the integer cursor `sync_time` crashed it there too.

Both images read the parity seed with the same configured catalogs (`databases/dynamodb/parity/`
in the skill: `make-read-catalog.py`, `run-read.sh`, `summarize-read.py`, `diff-records.py`). On the
110 readable tables (1316 records: every attribute type, nested maps and lists, composite, numeric
and binary keys, 1200 items, 105 paging tables) the records are identical after normalizing the two
deliberate differences below; an incremental sync resumed from a legacy state message (`str >
"hello"`) returns the same 2 records and the same cursor (`world`, count 1) on both sides.

| Case | Legacy 0.3.11 | source-dynamodb-v2 |
|---|---|---|
| `N` value beyond a `long` (`123456789012345678901234567890`) | `1.2345678901234568E29` (parsed as `double`, lossy) | exact `123456789012345678901234567890` |
| attribute absent from an item | absent from the record | `null` (the Bulk CDK fills every schema field) |
| attribute that is a reserved word (`dec`, `int`, `list`, `map`, `name`, ...) or contains `-`/`.` | `ValidationException` unless listed in `reserved_attribute_names`; `field.name` + `field-name` together can never be read (`Duplicate key #dyndb_fieldname`) | read without configuration (every attribute is aliased) |
| incremental with an `integer` cursor | crashes before the first record (`No enum constant JsonSchemaPrimitive.INTEGER`, confirmed live) | works; `number` cursors are accepted too |
| empty table configured (`"properties": {}`) | `ValidationException: Invalid ProjectionExpression: The expression can not be empty`, sync fails | stream dropped at catalog validation (`STARTED`, `INCOMPLETE`, error trace), the other streams are read and the sync exits 0 |
| configured table that no longer exists | `ResourceNotFoundException`, sync fails | same as the empty table: dropped, others read |
| stream statuses | `STARTED`, `RUNNING`, `COMPLETE` | `STARTED`, `COMPLETE` (the Bulk CDK never emits `RUNNING`) |
| full refresh state | none | `{"scan":...}` checkpoints and a final `{"scan_complete":true}` |
| incremental state message | `stream_state` with `stream_name`/`stream_namespace`, plus a `data` duplicate | `stream_state` with `cursor_field`, `cursor`, `cursor_record_count` only |

Everything else in `check` and `discover` is identical, legacy quirks included: `N` values are
`integer` only when they parse as a Java `long`, lists get one `anyOf` entry per element, the last
scanned item wins when an attribute has several types, only the partition (HASH) key is reported as
primary key, and only the first ~1000 scanned items are sampled.
