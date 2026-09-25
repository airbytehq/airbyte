# Contributing to source-dynamodb

`source-dynamodb` 1.0.0 is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core, no toolkits) rewrite of the
legacy Java connector (versions 0.3.x, last release 0.3.11). The legacy connector is the parity oracle: `spec`, `check`
and `discover` output and saved configurations must stay compatible with it.

## Build and test

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21 2>/dev/null || echo /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home)
./gradlew :airbyte-integrations:connectors:source-dynamodb:compileKotlin
./gradlew :airbyte-integrations:connectors:source-dynamodb:test      # unit tests (Testcontainers, needs Docker)
./gradlew :airbyte-integrations:connectors:source-dynamodb:assemble  # builds airbyte/source-dynamodb:dev
```

Unit tests start the official `amazon/dynamodb-local` image through Testcontainers, so no AWS
account is needed. DynamoDB Local accepts any access key and does not enforce IAM, which is why the
`ignore_missing_read_permissions_tables` behavior can only be exercised against the real service.

## Running the connector locally

```bash
docker run --rm airbyte/source-dynamodb:dev spec
docker run --rm -v $PWD/secrets:/secrets airbyte/source-dynamodb:dev check --config /secrets/config.json
docker run --rm -v $PWD/secrets:/secrets airbyte/source-dynamodb:dev discover --config /secrets/config.json
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

Every configured table is one stream feed. A table is read as one or more **parallel-scan
segments** (`Scan` with `Segment`/`TotalSegments`): DynamoDB assigns every item to a segment by
hashing its partition key, so the segments are disjoint, cover the table, cost nothing to compute
and need no boundary scan. The segment count is sized once per READ from `DescribeTable`'s
`TableSizeBytes` (free; AWS refreshes it about every 6 hours): one segment per
`airbyte.connector.extract.dynamodb.segment-target-bytes` (default 64 MiB), at most
`airbyte.connector.extract.dynamodb.max-segments` (default 128); tables below one target are
scanned as one segment. A table that `DescribeTable` reports at 0 bytes (empty, or loaded since
the last refresh: a 1 GB table seeded 40 minutes earlier still showed `TableSizeBytes: 0`) gets as
many segments as the effective concurrency, which costs one empty `Scan` per segment when the
table really is empty and keeps a freshly loaded large table parallel. Measured on a 1 GB table, 16 segments read 10x faster than one for the
same consumed read capacity. Each segment is one CDK partition; the `concurrency` setting (default
1 on STDIO, the socket count in speed mode) bounds how many segments and tables scan at once, so
with the default a table's segments are read one after another, which is still correct, and
tables are still read concurrently with each other.

The partition reader issues `Scan` requests page by page (`ExclusiveStartKey` = the previous page's
`LastEvaluatedKey`, with the partition's `Segment`), projecting exactly the attributes of the
configured stream. Every attribute is referenced through a placeholder (`#a0, #a1, ...` in
`ExpressionAttributeNames`), so reserved words and special characters need no configuration
(`reserved_attribute_names` is kept for backward compatibility and ignored).

Items are converted to JSON like the legacy `DynamodbAttributeSerializer`: `S` string, `N` number
(a `long` when it fits, otherwise the exact decimal), `B` base64 string, sets and lists as arrays,
`M` as an object, `BOOL`, `NULL`. Attributes an item does not have are emitted as `null`.

**Checkpoints.** The progress of every segment (its last `LastEvaluatedKey` or a complete marker,
and for incremental streams its running cursor maximum) lives in one registry per table
(`DynamoDbTableScan`), seeded from the saved state on the first round and updated after every
fully emitted page. A checkpoint is a snapshot of the whole registry, so every emitted state is a
valid resume point: a key that is a page behind only causes a re-read, never a gap. The CDK applies
the checkpoints of a round in partition order, each replacing the stream state, so the state that
survives a round is the last partition's snapshot; readers start in partition order, so the last
partition starts last and, once its own segment is complete, waits for the round's other readers to
stop (or its own deadline) before returning, which makes its snapshot the freshest and lets the
terminal state go out in the round in which the last segment completes. If its snapshot still
predates another segment's completion, the next round consists of one reader that emits nothing
but the terminal state (`DynamoDbTerminalStateReader`). A segment count is fixed for the life of a
table's scan (a `LastEvaluatedKey` is only valid for the `TotalSegments` that produced it) and is
saved in the state, so a resumed scan keeps it whatever the current table size or `concurrency`.

The stream state (`stream_state`) is backward compatible with the legacy `DbStreamState`:

| Situation | `stream_state` |
|---|---|
| Incremental scan complete (also what the legacy connector emitted) | `{"cursor_field":["updated_at"],"cursor":"2024-05-01T10:00:00Z","cursor_record_count":1}` |
| Incremental scan in progress (checkpoint after a round of pages; `checkpoint_target_interval_seconds`, default 300) | the fields above (the lower bound the scan filters on) plus `"scan":{"total_segments":3,"segments":[{"segment":0,"exclusive_start_key":{"pk":{"S":"..."}},"max_cursor":"...","max_cursor_record_count":1},{"segment":1,"complete":true,"max_cursor":"...","max_cursor_record_count":2},{"segment":2}]}` (a segment with neither key nor `complete` has not started) |
| Full refresh in progress | `{"scan":{"total_segments":3,"segments":[{"segment":0,"exclusive_start_key":{...}},{"segment":1,"complete":true},{"segment":2}]}}` |
| Full refresh complete (legacy emitted no state for full refresh) | `{"scan_complete":true}` |

The single-scan shape written before segments existed (`"scan":{"exclusive_start_key":{...},
"max_cursor":"...","max_cursor_record_count":1}`) is still read, as segment 0 of 1.

Incremental sync keeps the legacy semantics and uses the same segments: the cursor is a top-level
`S` or `N` attribute, every segment's scan filters on `cursor > :saved` (`>=` when the saved value is
a bare date such as `2016-02-15`), the whole table is still scanned and billed, the highest cursor
value seen in any segment becomes the next cursor once every segment is complete (the records
sharing it are counted across segments; the saved cursor and its count stay when nothing newer was
found), and a changed cursor attribute starts over. A legacy state (with its
`stream_name`/`stream_namespace` and the `data` duplicate) is read as is, so existing connections
resume without a reset. An `exclusive_start_key` is written in DynamoDB JSON and typed by the
table's key schema (`S`, `N`, `B`).

## Relationship with versions 0.3.x

1.0.0 keeps the legacy property names (`credentials` with `auth_type: "User"`,
`access_key_id`, `secret_access_key`, `endpoint`, `region`, `reserved_attribute_names`,
`ignore_missing_read_permissions_tables`), so a legacy access-key configuration loads unchanged
(`DynamoDbSourceSpecTest.testLegacyAccessKeyConfigurationStillLoads`). The spec itself deliberately
differs from the legacy one (decision of 2026-09-17: credentials must come from the configuration):

| | 0.3.11 (legacy) | 1.0.0 |
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

`src/test/resources/legacy-spec.json` is the `spec` output of the legacy `airbyte/source-dynamodb:0.3.11`
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
for `check` and, up to the schema shapes described below, identical catalogs for `discover`. With deliberately wrong credentials the new
connector reports: wrong secret -> "The secret access key is invalid ..."; unknown access key id or
bogus session token -> "The access key id or the session token is invalid ..." (AWS uses the same
message for both); a role the key may not assume -> the STS `AccessDenied` message naming the caller
and the role. Legacy returned `FAILED` without a message in all three cases.

- `src/test/resources/expected-catalog.json` is the `CATALOG` object the legacy image produced for the
  seed data in `src/test/resources/parity-seed.json`; `DynamoDbSourceDiscoverTest` seeds a DynamoDB
  Local container with the same data and asserts JSON equality after sorting streams by name and
  rewriting the legacy schema shapes into the canonical ones (next bullet).
- **Schema shapes (deviation, 2026-09-24).** The connector writes its JSON schemas in the canonical
  Bulk CDK shapes, as every other Bulk connector does: `{"type": "string"}` where the legacy connector
  wrote `{"type": ["null", "string"]}`, `{"type": "number", "airbyte_type": "integer"}` where it
  wrote `{"type": ["null", "integer"]}`, `{"type": "array", "items": {...}}` for sets and lists,
  `{"type": "object", "properties": {...}}` for maps; nullability is not expressed. The attributes,
  their types (`N` is an integer only when the sampled value parses as a `long`, sets are arrays,
  lists get one `anyOf` entry per element, maps recurse) and everything else in the catalog are the
  legacy connector's. Reason: the Bulk CDK re-derives each field's type from the configured catalog at
  READ time (`StateManagerFactory.airbyteTypeFromJsonSchema`) and understands a textual `type` only,
  so with the legacy shapes every attribute would be a JSONB field; the team chose the canonical
  shapes over a CDK change so that no other connector or catalog is touched. A configured catalog
  saved from the legacy connector (or from this connector before the change) keeps working: its
  `["null", ...]` shapes derive as JSONB on both sides (`DynamoDbFieldType.airbyteSchemaTypeOf` is a
  copy of the CDK's rules) and the records flow as JSON exactly as before until the user refreshes
  the schema, after which the fields carry their real types (which matters on the protobuf data
  channel only, see "Speed mode"). Migrating a legacy connection therefore shows a schema change for
  every column at the next refresh.
- Scripts to run both Docker images against one DynamoDB Local container live in the
  `new-database-source-connector` skill (`databases/dynamodb/parity/`).

| Case | Legacy 0.3.11 | 1.0.0 |
|---|---|---|
| `check` failure | `FAILED` with no message (vendor error only in logs) | `FAILED` with a classified message inside "Could not connect with provided configuration. Error: ..." plus an error `TRACE` (`application.yml` regex rules) |
| `check` with zero tables | `SUCCEEDED` | fails with "Discovered zero tables." (`CheckOperation`) |
| `check` without the `credentials` property | NPE message | "Missing required 'credentials' property ..." |
| `discover` of an empty table | stream with `"properties": {}` | stream dropped (`DiscoverOperation` skips streams without fields) |
| `discover` schema shapes | `{"type": ["null", "string"]}`, `{"type": ["null", "integer"]}` | `{"type": "string"}`, `{"type": "number", "airbyte_type": "integer"}` (canonical Bulk CDK shapes, see above) |

### read parity (verified 2026-09-17 on DynamoDB Local 3.3.1 and on a real AWS account vs 0.3.11)

Against the real account (us-east-2) with the `abv2_*` datasets seeded by the skill's
`parity/seed-aws.py` (10 tables, 215,213 items: every attribute type, reserved words, composite /
numeric / binary keys, an empty table, 5,000 dated items, 10,000 mixed 1 KB items, 200 items of
300 KB, and 200,000 items over 100 partitions) the two images return identical records on the 8
tables legacy can read (215,211 records; strict differences are only the explicit nulls and the
exact big numbers), identical records and states for incremental syncs on a bare-date, an ISO
timestamp and a 200,000-item string cursor, and the integer cursors legacy crashes on work. A state
handoff on the 200,000-item table works both ways (zero new records), a full refresh resumed from
a saved key after record 100,000 returns exactly the remaining 100,000 in order, and with
`checkpoint_target_interval_seconds: 1` and `concurrency: 4` the three big tables emit 48 mid-scan
states with every record exactly once (38 s, against 59 s one table at a time and 67 s for legacy).

Against the original 4 tables of that account (6 items) both images return byte-identical records
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

| Case | Legacy 0.3.11 | 1.0.0 |
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

## Speed mode (socket data channel)

`metadata.yaml` declares `connectorIPCOptions.dataChannel` with `JSONL` and `PROTOBUF` over `SOCKET`
and `STDIO`. The partition reader routes records through the CDK's `OutputMessageRouter`, acquires
one `RESOURCE_OUTPUT_SOCKET` per running partition and reports its partition id in every checkpoint,
so states over the sockets carry `partition_id`. Without a configured `concurrency`, speed mode
reads one table per socket (`concurrency` = number of socket paths); on STDIO the default is 1.

Fields are typed (`DynamoDbFieldType.airbyteSchemaTypeOf`, the CDK's own derivation of a type from
a JSON schema): `S` STRING, `B` BINARY, `BOOL` BOOLEAN, an integral `N` INTEGER, any other `N` NUMBER,
`NULL` NULL, `M` JSONB, `SS`/`NS`/`BS` arrays of STRING/NUMBER/BINARY, `L` an array of JSONB. On the
protobuf channel a value travels typed (`DynamoDbJsonNodeCodec.valueForProtobufEncoding`): a string
as a string, an integer as an exact integer (a 30-digit `N` as a big integer), any other number as
an exact decimal in plain notation (`100000`, `-0.0000001`, never `1E+5`), a boolean, a binary as
the bytes the CDK encodes as their base64 string, a DynamoDB `NULL` and an absent attribute as a
protobuf null; maps, lists and sets travel as JSON text produced by the CDK's `Jsons` mapper (plain
decimals included). `DynamoDbProtobufEncodingTest` covers every attribute type and the plain-number
rule on both channels.

**Mismatched values.** The schema comes from a sample, so an item may hold a value of another type
than its field declares (`flexible` is a string in one item and a number in another in the parity
seed; the last sampled item wins). On the JSON channels the value is emitted as is, as the legacy
connector did, and the destination coerces it. On the protobuf channel the slot is typed and cannot
hold it, so `DynamoDbPartitionReader` sends the field as null and adds a change record to the
message (`NULLED`, `SOURCE_SERIALIZATION_ERROR`), which the destination writes to `_airbyte_meta`;
`DynamoDbSourceSpeedModeReadTest.testProtobufOverSockets` asserts both. A field typed JSONB (a map,
or any field of a catalog configured with the legacy `["null", ...]` shapes) holds anything, so
such catalogs never produce change records.

Bulk CDK 1.1.11 could not build a protobuf record for a stream without a namespace
(`FeedBootstrap.ProtoEfficientStreamRecordConsumer` called `setStreamNamespace(null)`) and its
protobuf consumer reused one record builder per stream while only overwriting the slots present in
a payload, so a sparse item inherited the previous item's attributes. Both are fixed in the CDK at
1.1.13, airbytehq/airbyte#86976 (this branch builds against the local CDK until it is published); the reader also puts an
explicit null in the payload for every attribute an item lacks and releases its resources if the
router construction throws, so it is safe on either version.

Running the image in speed mode locally (Unix sockets do not cross the Docker Desktop VM boundary, so
the destination side has to be a container sharing a named volume):

```bash
docker volume create ddb-sock && docker run --rm -v ddb-sock:/sockets alpine chmod 1777 /sockets
# one sink per socket, connecting as soon as the connector binds the file
docker run -d --name sink0 -v ddb-sock:/sockets -v "$PWD/secrets:/work:ro" python:3.12-alpine \
  python -c 'import socket,os,time,sys; p="/sockets/s0"
while not os.path.exists(p): time.sleep(.1)
s=socket.socket(socket.AF_UNIX); s.connect(p); n=0
while (b:=s.recv(65536)): n+=len(b)
print(n,"bytes")'
docker run --rm -v "$PWD/secrets:/secrets:ro" -v ddb-sock:/sockets \
  -e DATA_CHANNEL_MEDIUM=SOCKET -e DATA_CHANNEL_FORMAT=JSONL -e DATA_CHANNEL_SOCKET_PATHS=/sockets/s0,/sockets/s1 \
  airbyte/source-dynamodb:dev read --config /secrets/config.json --catalog /secrets/catalog.json
```

Records then arrive on the sockets (with `partition_id`), states and stream statuses on the sockets
and on stdout. Verified on 2026-09-24 against DynamoDB Local with JSONL: 505 records over two sockets
(one table per socket at concurrency 2), 3 states, every stream `COMPLETE`, plain numbers on the wire.
## Scale validation on a 1 GB table (2026-09-24)

Table `abv2_1gb` in the test account (`us-east-2`, on-demand): 1,000,000 deterministic items of
~1 KB, 1,000 partition keys x 1,000 sort keys, seeded with the skill's `parity/seed-aws-1gb.py`
(~$1.25 of writes, ~$0.25/month, ~$0.03 per full scan). Everything below ran from a laptop on a
residential link, where one 1 MB `Scan` page takes ~0.4 s to arrive; in-region numbers are several
times higher, the ratios are what the design rests on. Harness: the connector's `installDist`
binary (`bin/source-dynamodb --read ...`, no image needed) with stdout streamed through a
summarizer that keeps `(pk, sk, sha1 of the record)` per record.

- **Segment probe** (plain SDK scans, `TotalSegments` = threads, same table): 1 segment 462 s,
  2: 195 s, 4: 118 s, 8: 64 s, 16: 44 s (10.5x); consumed read units identical at every N
  (124,274 = 128.5 per page); per-segment item counts sum exactly to 1,000,000 in every run.
- **Connector, full refresh** (`checkpoint_target_interval_seconds: 30`, `DescribeTable` still
  reported 0 bytes for the fresh table, so segments = concurrency): concurrency 16 -> 44.6 s
  (29 states), 8 -> 72.3 s, 4 -> 117.3 s, 1 -> 466.7 s (one segment); a state every 30 s for
  every running segment; final state `{"scan_complete": true}` every time. Peak RSS 600-750 MB
  with `-Xmx1g`; **concurrency 16 with `-Xmx384m`: 37.5 s, peak RSS 469 MB**, no OOM.
- **Kill and resume** (concurrency 8, `kill -9` of the JVM at 42 s): run 1 emitted 648,332
  records and 8 states, the last one with a resume key for each of the 8 segments; run 2 from
  that state emitted 504,702 records and finished with `scan_complete`; union by `(pk, sk)` =
  1,000,000 distinct keys, 0 missing, 153,034 duplicates = exactly the records of run 1 after its
  last checkpoint (the 10 s between the 32 s checkpoint and the kill).
- **Incremental over segments** (concurrency 8): first sync on `updated_at` 1,000,000 records in
  70.7 s, terminal state `{"cursor_field": ["updated_at"], "cursor": "2024-01-12T13:46:39Z",
  "cursor_record_count": 1}`; the next sync from that state read 0 records in 14.3 s (the filtered
  scan still visits every item but transfers nothing) and kept the state; first sync on the
  integer cursor `seq` -> `"cursor": "999999"`, count 1, 64.4 s.
- **State compatibility**: a state written by the previous single-scan build
  (`{"scan": {"exclusive_start_key": {...}}}` after 55,362 of 200,000 items of `abv2_large`)
  resumed to exactly the remaining 144,638 records.
- **Content parity**: the `(pk, sk, sha1)` multisets of the sequential read, the 16-segment read,
  the incremental first sync and the legacy `source-dynamodb:0.3.11` read of the same table are
  identical.
- **Sequential read vs legacy**: on the 1 GB table the legacy 0.3.11 image took 258 s and 379 s in
  two runs and the new connector's single-segment read 466.7 s and 265.8 s (runs an hour apart,
  interleaved with the legacy ones): both sit at the single-`Scan` ceiling of the link, whose page
  latency swung by ~50% during the afternoon. A probe of the SDK's sync HTTP clients on the same
  80 pages (apache5 = the 2.54.20 default, apache 4 = the legacy default, url-connection, and the
  legacy image's own SDK 2.18.1) gave 26-34 s each with no consistent ranking, so the HTTP client
  is not a factor and the default stays.
