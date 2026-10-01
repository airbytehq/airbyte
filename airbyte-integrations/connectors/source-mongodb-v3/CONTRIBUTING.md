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

- `src/test/resources/expected-spec.json` is a snapshot of this connector's generated `spec`;
  `MongoDbSourceSpecTest` fails if it drifts. It keeps v2's property names, titles, descriptions,
  defaults and `database_config` oneOf so saved v2 configurations load unchanged, minus the two
  dropped Debezium-only properties. Rendering follows the Bulk CDK generator like every other Bulk
  CDK source (`"type": "object"` on oneOf variants, discriminators as a single-value `enum` +
  `default`, no `changelogUrl`) — byte-for-byte parity with v2's hand-written `spec.json` is not a
  goal, so there is no spec post-processing.
- To compare `check` against the legacy image, start an auth-enabled single-node replica set on a
  Docker network (recipe in the `new-database-source-connector` skill, `databases/mongodb/README.md`)
  and run both images on that network with the same `--config` files:

  ```bash
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb-v2:2.0.7 check --config /configs/case.json
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb-v3:dev   check --config /configs/case.json
  ```

  Success output is identical. On failure the Bulk CDK adds an error `TRACE` message and wraps the
  message in "Could not connect with provided configuration. Error: ..."; the wrapped message
  matches the legacy one for every case, including "no authorized collections": the querier
  throws v2's message naming the unreadable databases from the last `streamNames()` call during
  `check`, before the CDK would fall back to its generic "Discovered zero tables.".
- `discover` parity: `src/test/resources/expected-catalog-*.json` are the `CATALOG` objects the
  legacy image produced for the seed data of `MongoDbSourceDiscoverTest` (every BSON type, `_id` of
  ObjectId/int/string, an empty collection, a view, a `system.*` collection, two databases), and the
  test asserts JSON equality after sorting streams by name (the legacy connector emits streams in
  hash order). Legacy quirks are reproduced on purpose: booleans, dates, timestamps, ObjectIds and
  binary data are all declared as `string`; ints/longs/doubles/decimals as `number`; arrays as
  `{"type":"array"}` without `items`; empty collections are omitted; views are included; every
  stream advertises `default_cursor_field: ["_ab_cdc_cursor"]` and `is_resumable: true`. A field
  seen with several BSON types takes the type of whichever document shape the server returns first,
  in both connectors. To diff the Docker images, run `discover` for both on the parity replica set
  and compare the `CATALOG` lines with streams sorted (scripts in the skill's
  `databases/mongodb/parity/`).
- `check` does not sample documents (the legacy `check` only ran `listCollections`);
  `MongoDbSourceMetadataQuerier.Factory` reads `airbyte.connector.operation` and returns no fields
  during `check`.

## Read

`read` supports full-refresh and incremental (snapshot + CDC) syncs.

- `MongoDbPartitionsCreatorFactory` plans the READ. Each `Stream` feed gets one
  `MongoDbSnapshotPartitionsCreator` (one partition per collection, no concurrent `_id` splitting —
  see "Concurrency" below); the `Global` feed gets one `MongoDbCdcPartitionsCreator`.
- **Snapshot** (`MongoDbSnapshotPartitionReader`): reads a collection ordered by `_id` and emits
  every document. `MongoDbRecordConverter` reproduces the legacy record shape (ObjectId hex, `Date`
  always with milliseconds, `Binary` as Base64, `BsonRegularExpression` as `(options)pattern`,
  `CodeWithScope` as an object, `MinKey`/`MaxKey` omitted, the `BsonTimestamp` epoch-millis quirk).
  It **resumes** from the checkpointed `_id` (`_id > lastSeen`), respects the
  `checkpointTargetInterval` timeout, and completes via `MongoDbSharedState.completedSnapshots`. The
  per-collection checkpoint is the legacy `MongoDbStreamStateValue` shape
  (`{id, status, idType, binarySubType}`): `COMPLETE` for an incremental stream once its snapshot
  finishes, `FULL_REFRESH` for a full-refresh stream. At READ time the metadata querier serves
  `fields()` from the configured catalog rather than re-sampling.
- **CDC** (`MongoDbCdcPartitionReader`, the `Global` feed): reads the replica-set change stream with
  the native driver `watch()` — **not Debezium**. Cold start captures a resume token before the
  snapshot; warm start drains available changes (insert/update/replace as upserts, delete with
  `_ab_cdc_deleted_at`) and checkpoints the new token in `MongoDbCdcState`. `update_capture_mode`
  selects `UPDATE_LOOKUP` vs `REQUIRED` (post-image, MongoDB 6.0+). **Legacy v2 state is read
  as-is:** `MongoDbCdcState.fromOpaqueStateValue` also understands v2's Debezium offset map
  (`{"state": {<key>: "{\"sec\":..,\"ord\":..,\"resume_token\":\"<hex>\"}"}, "schema_enforced": ..}`)
  and extracts `resume_token`, which is the server's own `_data` that Debezium stored verbatim — so
  an upgraded connection resumes from where v2 left off with no reset or migration. v3 writes its
  native shape going forward. A saved token the server rejects
  (oplog rolled past it — `ChangeStreamHistoryLost` — or unparseable) honours
  `invalid_cdc_cursor_position_behavior`: `Fail sync` raises the legacy "Saved offset is not valid…"
  config error; `Re-sync data` resets the CDC and snapshot state and re-snapshots. Note the server
  accepts any *well-formed* token, even for a nonsensical cluster time, and resumes from the oplog
  start — only a rejected token can be detected.
- **Consistency guards** (ported from v2, run when planning the READ): the `schema_enforced` mode must
  agree between the configuration, the configured catalog and the saved CDC state; and each stream's
  configured sync mode must agree with its saved snapshot status (`INCREMENTAL` ↔
  `IN_PROGRESS`/`COMPLETE`, `FULL_REFRESH` ↔ `FULL_REFRESH`). Both raise an actionable config error
  telling the user to reset.
- **Wire projection**: under `schema_enforced` the snapshot `find()` projects only the catalog's
  fields, so documents' extra fields never cross the network.
- **TLS**: `ATLAS_REPLICA_SET` enables TLS on the client (Atlas requires it; v2 forced
  `mongodb.ssl.enabled=true` on its CDC path). Self-managed clusters honour the connection string.
- **`BSONObjectTooLarge`** (server error 10334, a change event over 16MB) is mapped by an
  `application.yml` classifier rule to the legacy actionable message.
- **WASS**: an incremental snapshot that exceeds `maxSnapshotReadDuration`
  (`initial_load_timeout_hours`) yields for the rest of the READ so the next sync's change-stream
  read advances the resume token before the snapshot resumes.
- **Socket / speed mode (protobuf)**: both readers emit through `OutputMessageRouter`, so records go
  over STDIO (JSONL) or the socket data channel (JSONL/PROTOBUF) per `airbyte.connector.data-channel`
  (declared in `metadata.yaml` `connectorIPCOptions.dataChannel`). Because MongoDB is schemaless, each
  value is wrapped in a per-type codec (`MongoDbRecordCodecs.kt`): the JSONL channel keeps the raw
  JSON value, while the protobuf channel coerces it to the field's declared `airbyteSchemaType` and
  nulls a value whose actual BSON type does not match (schema/value mismatch is possible on a
  schemaless store). The payload carries every schema field (null for absent) so the protobuf
  consumer's positional encoding is correct.

### Concurrency

One partition per collection, read on one thread (collections are still read in parallel with each
other by the CDK). Splitting a single collection into concurrent `_id` ranges is **not** implemented:
there is no evidence that two parallel range reads beat one ordered scan on a replica set, and the
`_id` boundaries cannot be computed without a scan (`$sample`/`splitVector` are approximate). This is
a later optimization gated on a measured speed-up (SKILL.md Phase 1, "Concurrency"; Stage 5).

### Testing

- Unit + Testcontainers tests cover spec/check/discover, full-refresh and incremental snapshot,
  mid-collection resume, native CDC (insert/update/delete), WASS, the record conversions, the
  protobuf encoding path (`MongoDbProtobufEncodingTest`), the invalid-resume-token behaviours, the
  schema-mode and sync-mode guards, and the exception-classifier rules
  (`MongoDbExceptionClassifierTest`).
- `MongoDbSourceAcceptanceTest` is the end-to-end acceptance flow (spec → check → discover → read with
  a datatype matrix); the Python CAT in `acceptance-test-config.yml` is bypassed (deprecated).

### Remaining work

- **Wire-level socket test:** the protobuf encoding is unit-tested end to end via
  `NativeRecordPayload.toProtobuf`, and the STDIO path is exercised by every read test through
  `OutputMessageRouter`; a full Unix-socket sink test (bind sockets, decode `AirbyteMessageProtobuf`
  frames, compare with STDIO) is still to add. Note the CDK protobuf-consumer fixes land in 1.1.13.
- **Terabyte-scale validation**: bounded-memory, kill/resume and throughput vs `source-mongodb-v2` on
  a very large collection — needs infrastructure not available here.
- **Record/state Docker parity** against `source-mongodb-v2` via `databases/mongodb/parity/`.

> **CDK version:** this branch pins `cdkVersion=local` and bumps
> `airbyte-cdk/bulk/core/extract/version.properties` to `1.1.12` because READ-time catalog
> validation NPE'd on `{"type":"array"}` without `items` (MongoDB arrays) up to 1.1.11. The one-line
> fix in `StateManagerFactory.airbyteTypeFromJsonSchema` must be published as `1.1.12` and the
> connector re-pinned to that version before this leaves draft — CI rejects `cdkVersion=local`.
