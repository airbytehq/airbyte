# Contributing to source-mongodb

Since version 3.0.0, `source-mongodb` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core, no
toolkits) connector. It replaced the Debezium-based Java implementation (versions ≤ 2.1.1, the
"legacy connector" below) in place, under the **same connector definition** (`definitionId
b2e713cd-…`, carried over as v2 carried it over from `source-mongodb`), so existing connections
upgrade with no clear or refresh. The legacy connector is the parity oracle: `spec`, `check`, `discover` and
`read` output, saved configurations and persisted state must stay compatible with it. The
user-facing documentation is `docs/integrations/sources/mongodb.md` (plus the migration and
troubleshooting pages next to it); keep it in step with behaviour changes.

## Build and test

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21 2>/dev/null || echo /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home)
./gradlew :airbyte-integrations:connectors:source-mongodb:compileKotlin
./gradlew :airbyte-integrations:connectors:source-mongodb:test          # unit tests (Testcontainers, needs Docker)
./gradlew :airbyte-integrations:connectors:source-mongodb:assemble      # builds airbyte/source-mongodb:dev
```

Unit tests start `mongo:7.0` containers through Testcontainers as a single-node replica set.
`check` only logs the cluster type, as the legacy connector did: `REPLICA_SET`, `SHARDED` (a cluster reached
through `mongos`) and `LOAD_BALANCED` (e.g. Atlas Serverless) support change streams; a `STANDALONE` `mongod`
has no oplog, so full refresh works there and an incremental sync fails when the change stream is opened
(`testCheckPassesAgainstStandaloneInstance`).

## Running the connector locally

```bash
docker run --rm airbyte/source-mongodb:dev spec
docker run --rm -v $PWD/secrets:/secrets airbyte/source-mongodb:dev check --config /secrets/config.json
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
    "auth_source": "admin"
  },
  "schema_enforced": true
}
```

## Parity with the legacy connector

- `src/test/resources/expected-spec.json` is a snapshot of this connector's generated `spec`;
  `MongoDbSourceSpecTest` fails if it drifts. It keeps the legacy property names, titles, descriptions, defaults and
  `database_config` oneOf so saved v2 configurations load unchanged, minus the dropped properties
  (`initial_waiting_seconds`, `queue_size`, `update_capture_mode`). `schema_enforced` stays inside the
  `database_config` variants, where v2 had it: the form then shows and re-saves a saved `false`, whereas a root
  field with a default would make the form inject `true` and drop the nested value on any edit, flipping a
  schemaless source into "refresh schema and reset". A root `schema_enforced` is still read, write-only, as a
  fallback for configurations saved by pre-release builds that had it there; the nested value wins. Rendering follows the Bulk CDK generator like every
  other Bulk
  CDK source (`"type": "object"` on oneOf variants, discriminators as a single-value `enum` +
  `default`, no `changelogUrl`) — byte-for-byte parity with v2's hand-written `spec.json` is not a
  goal, so there is no spec post-processing.
- To compare `check` against the legacy image, start an auth-enabled single-node replica set on a
  Docker network (recipe in the `new-database-source-connector` skill, `databases/mongodb/README.md`)
  and run both images on that network with the same `--config` files:

  ```bash
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb-v2:2.1.1 check --config /configs/case.json
  docker run --rm --network mongo-v3-net -v $PWD/configs:/configs airbyte/source-mongodb:dev   check --config /configs/case.json
  ```

  **Record parity** (`parity/seed-values.js`, `diff-records.py`, `run-read-tls.sh` in the skill):
  both images read the same seeded database — every BSON type with edge values (doubles down to
  `5e-324` and `-0.0`, `NaN` and the infinities of both number kinds, dates at epoch, before 1970 and
  beyond year 9999, long min/max, binary subtypes 0/1/2/3/5/9/128, regex options, control characters,
  `undefined`/`MinKey`/`MaxKey` inside documents and arrays), `_id`s of ObjectId/int/long/string/
  UUID/binary/document, a field whose type varies across documents, a scalar in an `array` field and
  an `_aibyte_transform` property — in both schema modes, plus an incremental round trip (snapshot,
  then insert/update/replace/delete, update-then-delete, delete-then-upsert, with and without
  pre-images) with each image resumed from its own state. Every value is identical except the three
  above; the only shape difference is that v2 omits a field absent from the document where the Bulk
  CDK emits it as `null`. The incremental read showed two semantic differences: an update whose
  document is gone by the lookup is a delete here but, when the collection stores pre-images, a
  stale **upsert** of the pre-image in v2 (the delete event that follows makes the final state the
  same); and `_ab_cdc_cursor` is the 64-bit cluster time where v2 wrote `<seconds><8-digit counter>`,
  so every record of this version out-ranks v2-era rows in destination dedup — the direction an
  upgrade needs. `_ab_cdc_updated_at` is at second precision on a change (the oplog time; v2 wrote
  Debezium's millisecond wall clock). v2 refuses a `double` `_id` collection, which this version
  reads. Running v2's CDC path needs TLS on the server: its Debezium properties hard-code
  `mongodb.ssl.enabled=true` (`run-read-tls.sh` trusts a self-signed CA through `JAVA_TOOL_OPTIONS`).
  Success output of `check` is identical. On failure the Bulk CDK adds an error `TRACE` message and wraps the
  message in "Could not connect with provided configuration. Error: ..."; the wrapped message
  matches the legacy one for every case, including "no authorized collections": the querier
  throws v2's message naming the unreadable databases from the last `streamNames()` call during
  `check`, before the CDK would fall back to its generic "Discovered zero tables.". A user with no
  privilege at all on a configured database gets the server's own `Unauthorized`, as with the
  legacy connector. **`listCollections` is two commands**: the names come from the form without a
  filter (`authorizedCollections: true, nameOnly: true`), the only form the server lets a user
  without the `listCollections` privilege run (it then lists what they can read), and the views and
  time-series collections to drop from a `type`-filtered form that needs the privilege — tolerated
  when missing, such a user has no views to read anyway. `MongoDbSourcePermissionsTest` runs these
  against a replica set with authentication (`MongoDbAuthReplicaSet`): `read` on one database,
  `readAnyDatabase`, `find` on one collection only, no privilege, a wrong password.
- `discover` parity: `src/test/resources/expected-catalog-*.json` started as the `CATALOG` objects
  the legacy image produced for the seed data of `MongoDbSourceDiscoverTest` (every BSON type, `_id`
  of ObjectId/int/string, an empty collection, a view, a `system.*` collection, two databases), and
  the test asserts JSON equality after sorting streams by name (the legacy connector emits streams
  in hash order). Most legacy quirks are reproduced on purpose: dates, timestamps, ObjectIds and
  binary data are declared as `string`; ints/longs/doubles/decimals as `number`; arrays as
  `{"type":"array"}` without `items`; empty collections are omitted; every stream advertises
  `default_cursor_field: ["_ab_cdc_cursor"]` and `is_resumable: true`. A field seen with several
  BSON types takes the type of whichever document shape the server returns first, in both
  connectors. Two legacy bugs are fixed rather than reproduced, so the fixtures differ from the
  legacy output there: booleans are declared as `boolean` (`$type` reports `bool`, which the legacy
  mapping never matched, so it fell through to `string` while the records carried real booleans), and views and
  time series collections are not streams (the legacy `listCollections` filter `{type: "collection"}` was appended
  to the command *result* instead of the command, so it never reached the server, and the legacy connector listed
  both: a full refresh snapshotted them thanks to `allowDiskUse`, an incremental stream never received a change
  since change streams cannot be opened on either, and a time series collection has no `_id` index, so every
  resumed round re-sorted the whole collection). The `type: collection` filter excludes them from discovery,
  documented as a breaking change (`testDiscoverExcludesViewsAndTimeSeriesCollections`); a stream still in a
  catalog fails the CDK's catalog validation until the schema is refreshed. Set
  `MONGODB_REGENERATE_FIXTURES=true` when running `MongoDbSourceDiscoverTest` to rewrite the
  fixtures from the actual output. To diff the Docker images, run `discover` for both on the parity
  replica set and compare the `CATALOG` lines with streams sorted (scripts in the skill's
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
  every document from one `find().sort(_id).allowDiskUse(true)` query per round, in batches bounded
  by the 16MB reply only (`batchSize(Int.MAX_VALUE)`; v2 split the scan into `limit(chunk)` rounds
  sized from `$collStats`, which this version does not need). A round ends when the collection is
  exhausted (the terminal checkpoint), when the CDK's `checkpointTargetInterval` (10 minutes)
  cancels it — the last `_id` is checkpointed and the next round resumes with `_id > last` — or
  when an incremental snapshot yields to CDC (WASS). A round that **fails** is not checkpointed
  (`FeedReader` checkpoints completed and timed-out partitions only), so a transient failure
  re-reads at most the interval's worth of documents on retry. Both readers take documents from the driver
  as `RawBsonDocument` (undecoded bytes) and `MongoDbRecordConverter` builds the record in one pass
  over them with a `BsonReader` (`MongoDbBsonValues`): a top-level scalar becomes the JVM value the
  protobuf encoder wants, a nested document or array is written straight to compact JSON text, which
  the JSON channel copies verbatim as a Jackson `RawValue` node and the protobuf channel sends as is
  (`MongoDbValue`). No `Document` or `JsonNode` tree is ever built; fields outside the catalog are
  skipped without being read. The reader itself (`BsonBinaryReader`) is now the dominant conversion
  cost — a bare walk of a document is about 60% of it; a hand-rolled walker over the bytes would be
  the next step if conversion ever mattered. The converter reproduces the legacy record shape (ObjectId hex, `Date`
  always with milliseconds and no sign on a year beyond 9999, `Binary` of **any** subtype as the
  Base64 of its raw bytes — UUIDs of subtype 3 and 4 and subtype-9 vectors included —
  `BsonRegularExpression` as `(options)pattern` or the bare pattern when there are no options,
  `CodeWithScope` as an object, `MinKey`/`MaxKey`/`undefined`/`DBPointer` omitted, the
  `BsonTimestamp` epoch-millis quirk). A `NaN` or infinite `double`/`Decimal128` has no JSON number:
  it is emitted as its name in text (`"NaN"`, `"-Infinity"`, as v2 did) and nulled on protobuf in a
  `number` field; a `Decimal128` negative zero, which no `BigDecimal` can carry, is the double
  `-0.0`. `MongoDbClientFactory` pins the driver's
  `uuidRepresentation` to `UNSPECIFIED` so that a `?uuidRepresentation=` in the connection string
  cannot make the driver decode binaries to `UUID` objects, which would change the emitted value
  and lose the subtype the `_id` checkpoint needs (the legacy connector had that hole). It also asks
  for wire compression (`snappy`, then `zlib`; `snappy-java` is on the classpath for it) unless the
  connection string carries a `compressors` option of its own — an empty one turns compression off.
  `testEveryBsonTypeIsEmittedAsDocumented` reads one document holding every BSON type through the
  connector in both schema modes (and once with `?uuidRepresentation=standard`) and asserts each
  field's value; `MongoDbBsonValuesTest` covers nested values, non-finite numbers and the binary
  reader agreeing with the in-memory one. Two v2 behaviours tied to the configured
  catalog are kept as well: a non-array value in a field declared `array` is wrapped in a
  one-element array (a present BSON `null` included → `[null]`) so the structural mismatch does
  not become `null` downstream; and a user-added `<field>_aibyte_transform` (string) catalog
  property receives the field's value JSON-stringified, with the original field nulled.

  Three conversions **intentionally differ** from v2 — keep them: `Decimal128` is emitted as the exact
  decimal (v2 went through `doubleValue()` and lost precision: `1.10` → `1.1`, `1E+3` → `1000.0`; a
  negative zero is `-0.0` on both), `Date` is always formatted in
  UTC (v2 used a `SimpleDateFormat` in the JVM default zone with a literal `Z`, only correct because the image runs in
  UTC), and `CodeWithScope` carries its scope (v2 emitted `"scope": {}` whatever the scope held).
  Everything else is byte-identical to 2.1.1 — see *Record parity* below. It **resumes** from the checkpointed `_id`, respects the `checkpointTargetInterval`
  timeout (10 minutes, `MongoDbSourceConfiguration.checkpointTargetInterval`: the CDK cancels the scan, the last `_id`
  is checkpointed and a new round resumes with `_id > last`), and
  completes via `MongoDbSharedState.completedSnapshots`. The per-collection checkpoint is the legacy
  `MongoDbStreamStateValue` shape (`{id, status, idType, binarySubType}`): `COMPLETE` for an
  incremental stream once its snapshot finishes, `FULL_REFRESH` for a full-refresh stream — with
  the last `_id` while the full refresh is under way, so a retry of the attempt resumes after it,
  and **no `_id` once it finished**, so the next sync starts over (the legacy contract: "full
  refresh streams that finished set their id to null"). Every checkpoint is written inside the
  GLOBAL state message, but the Bulk CDK seeds a full-refresh stream's current state from STREAM
  messages only, so `MongoDbSharedState.fullRefreshInputState` reads it from the GLOBAL input
  state where it was written (`testFullRefreshResumesWhenInterruptedAndStartsOverWhenFinished`).
  A catalog without incremental streams still writes a shared state (`MongoDbSchemaModePartitionReader`:
  the schema mode, and any position a previous sync saved), because the CDK cannot be given a
  GLOBAL state without `shared_state` back (`testFullRefreshOnlySyncStateCanStartAnIncrementalSync`). `idType`
  keeps v2's values — `OBJECT_ID`, `STRING`, `INT`, `LONG`, `BINARY` (UUID text for subtype 4,
  Base64 otherwise) and, since v2 2.1.0, `OBJECT` (a document `_id` as extended JSON) — and adds
  `DOUBLE` and `DECIMAL` (the number's own text, `Decimal128.parse` is exact), `DATE` (epoch
  milliseconds) and `TIMESTAMP` (the 64-bit value), so those `_id`s resume as their native BSON
  type (`MongoDbStreamStateValueTest` round-trips every type, NaN/-0.0/±Infinity included;
  `testTypedIdCollectionsResumeMidSnapshot` resumes a collection of each `_id` type — string,
  int32, int64, binary, UUID subtype 4 and 3, double, decimal, date, timestamp — against the server
  after a forced mid-collection checkpoint). Any other `_id` kind (code, symbol, bool, …)
  checkpoints as `idType: BSON`, the extended JSON of `{"v": <id>}`, and resumes as the parsed
  `BsonValue` — typed, because comparison operators only match values of the operand's type, so a
  text fallback would make `_id > "…"` match nothing and silently end the collection
  (`testOtherIdKindsResumeMidSnapshot`, JavaScript `_id`s). A stream state that is present but cannot be parsed fails the sync with the
  same "Failed to migrate to the new connector version state protocol" error as an unreadable
  CDC state (`MongoDbStateMigration`), rather than silently restarting the snapshot; absent,
  JSON-null and empty `{}` states mean "no checkpoint".

  **Diagnostics** (`MongoDbDiagnostics`): three lines built from cheap server calls, each logged once
  — the connection (`hello` + `buildInfo`: version, topology, the member answering and its role,
  hosts, wire version, TLS, read preference, requested compression) when a client is created, for
  `check`, `discover` and `read` alike; the oplog (the `collStats` command on `local.oplog.rs` and
  its oldest and newest `ts`: size, entry count, window, and where the saved position stands in it,
  the token decoded inside the guarded call so a malformed one fails the line, not the sync) once
  per READ before the change stream is read; and each collection (`collStats`, which totals the
  shards through a `mongos`, plus the kind of its smallest `_id`) once per stream per READ as its
  snapshot starts, so a resumed round stays silent and the next sync logs again. The once-guards
  live in `MongoDbSharedState`. A call that fails is one `WARN` with the server's message and the
  sync goes on — expected for a user without `local` access (the oplog line) or with
  collection-level privileges only. The `collStats` command (deprecated since 6.2, still served by
  8.0) is used rather than the `$collStats` stage so that no diagnostic is an `aggregate`: the
  failpoint tests on `aggregate` must keep hitting the change stream, not a diagnostic. Three traps:
  `collStats` returns a size as `Int` while it fits and `Long` past that (read them as `Number`;
  v2's oplog log died on that cast and never logged); kotlin-logging swallows an exception thrown
  inside a message lambda into an INFO, so a line that may fail is built *before* `log.info {}`
  (`logGuarded`); and nothing computed for a diagnostic may run outside the guard.
  **One `_id` kind per collection is assumed.** The resume filter is a plain
  `{_id: {$gt: <checkpoint>}}`, which MongoDB type-brackets: it only matches `_id`s of the
  checkpoint's own BSON type, so a collection mixing e.g. integer and string `_id`s reads every
  document in an uncut round but only the integers after a checkpoint on one. This is v2's
  behaviour, reproduced exactly: `MongoDbIdTypes.present` is a port of 2.1.1's
  `InitialSnapshotHandler.getIdFieldTypes` (the smallest and largest `_id` from two covered index
  seeks pin one type; otherwise one `$type` probe per candidate), run once per stream per READ as
  part of the collection diagnostic (`_id types [number, string]`), and a mix logs v2's warning
  "The _id fields in this collection are not consistently typed, which may lead to data loss" and
  emits v2's `db-sources-mongo-multiple-id-types` analytics trace; it does not fail
  (`testMixedIdKindsReadWholeUncutAndOneKindAfterACheckpoint`, `MongoDbIdTypesTest`). One
  deliberate difference: numbers of any width (`int`, `long`, `double`, `decimal`) are one kind,
  as they are for the comparison — drivers routinely mix them (`testNumericIdWidthsAreOneType`) —
  where v2 warned about `int` + `double` too. At READ time the metadata querier serves
  `fields()` from the configured catalog rather than re-sampling.
- **CDC** (`MongoDbCdcPartitionReader`, the `Global` feed): reads the change stream with the native
  driver `watch()` — **not Debezium**. With one configured database the stream is opened on that
  database (`db.watch()`), which the `read` role allows; with several it is cluster-wide
  (`client.watch()`, needs `readAnyDatabase`) — v2's privilege model since 2.0.2, verified against an
  auth-enabled replica set (a `read`-only user gets `Unauthorized` on the cluster-wide stream).
  `testCdcAcrossMultipleDatabases` covers the cluster-wide path. Cold start captures a resume token before the snapshot;
  warm start emits the available changes (insert/update/replace as upserts, delete with
  `_ab_cdc_deleted_at`) and checkpoints the new token in `MongoDbCdcState`. On MongoDB 6.0+ the stream asks for
  `fullDocumentBeforeChange: whenAvailable` (the legacy
  `change_streams_update_full_with_pre_image` capture mode): a delete carries the pre-image when the collection stores
  one, else `_id` only; an update/replace whose `fullDocument` is null (the document was deleted before the lookup) is
  emitted as a delete, not dropped (`testDeletesCarryPreImageAndUpdateOfDeletedDocumentIsADelete`; v2 emitted it as
  an `_id`-only delete, or as an upsert of the pre-image when the collection stored one). The server fetches
  a pre-image for every event once they are requested, so the pipeline (`MongoDbChangeStreamPipeline`) `$$REMOVE`s it
  from the events emitted from `fullDocument`: only deletes and lookup-less updates carry one over the network
  (`MongoDbChangeStreamPipelineTest` watches a raw stream through the pipeline). The read is
  **bounded**:
  the reader first takes the cluster time the server gossips (`hello`'s `$clusterTime`, at or past every write
  committed on every shard — a fresh cursor's post-batch token is the minimum over the shards through `mongos`
  and lags on an idle shard) and stops after the first event past it, or on an empty batch once the post-batch
  token has reached it — through `mongos` an empty batch can precede committed events the router holds back until
  every shard has passed them, so the reader polls on (bounded by `MAX_EMPTY_POLLS`) — checkpointing that
  event's own token — a resume reads strictly after a token, so nothing is lost or repeated and a busy cluster cannot
  keep the sync open
  (`testCdcStopsAtTargetUnderContinuousWrites`). The token is checkpointed once, when the read ends. A catalog without
  incremental streams gets no CDC partition at all. A view, time series collection or dropped
  collection left in the catalog fails the CDK's catalog validation until the schema is refreshed —
  documented in the migration guide. `_ab_cdc_cursor` is a
  MongoDB oplog time as a long (`BsonTimestamp.value`), stamped per record by the readers: the
  event's own time on a change, the time of the change-stream position this READ saved
  (`MongoDbCdcState.cdcSyncedUntil`, decoded from the captured or checkpointed token and
  persisted with it; the snapshot readers take it from the `Global` feed's checkpoint, to the
  second) on a snapshot row. Every event a later sync replays is strictly after that position, so a change
  always sorts above the snapshot row it supersedes whichever node served the snapshot (the
  gossiped `$clusterTime` would not do: it can run ahead of a lagging secondary's applied ops), and
  a re-read event keeps its cursor. `_ab_cdc_updated_at` is the event's cluster time on a change and the sync's `emittedAt`
  on a snapshot row, like the other Bulk sources. The stream is opened with `fullDocument: updateLookup` —
  the legacy default and now the only behaviour (`update_capture_mode` is dropped from the spec; a saved value is
  ignored):
  no post-image prerequisite on the collections, at the cost of intermediate states of a document updated several times
  between reads. The `$match` names the `ns.db` / `ns.coll` of every stream that has a checkpoint
  (snapshot started or complete; the `{}` the CDK writes for a stream that has not checkpointed yet is not one,
  `testEmptyPlaceholderStreamStateIsNotACheckpointForTheChangeStream`) — the legacy connector's Debezium include
  list, logged at the start of every read with the deferred streams — so events of
  unselected collections never leave the server and a stream snapshotted for the first time in a
  sync is not also replayed from the token (it joins the `$match` from the next sync;
  `testStreamAddedToAWarmConnectionIsSnapshottedOnceNotReplayedToo`); with nothing to watch, on a
  cold start, the match names no namespace; `batchSize` is maxed so batches are bounded by
  the 16MB message size only; the cursor carries the comment
  `airbyte-source-mongodb` for `currentOp`. **Legacy v2 state is read
  as-is:** `MongoDbCdcState.fromOpaqueStateValue` also understands v2's Debezium offset map
  (`{"state": {<key>: "{\"sec\":..,\"ord\":..,\"resume_token\":\"<token>\"}"}, "schema_enforced": ..}`)
  and extracts `resume_token`: Debezium stores the server's own token, as the hex `_data` string
  (Debezium 2.x, v2 ≤ 2.0.x) or as the base64-encoded BSON of the token document (Debezium 3.x,
  v2 ≥ 2.1.0) — both are accepted — so an upgraded connection resumes from where v2 left off with
  no clear, refresh or migration. **Downgrade path:** the legacy `state` and `schema_enforced` are carried
  into every later checkpoint byte-for-byte and never updated (`MongoDbCdcState.of(…, prior)`;
  `testLegacyVariablesAreCarriedVerbatimAndNeverUpdated`), while `resumeToken` is the only position
  3.0.0 reads (used when present, created from the legacy offset otherwise). Pinned back to 2.1.1, a
  connection resumes from its pre-upgrade position and replays what happened since; a reset
  (`Re-sync data`) or a connection born on 3.0.0 carries no legacy variables, so 2.1.1 would start
  afresh. Documented in the migration guide. A saved token the server rejects
  (oplog rolled past it — `ChangeStreamHistoryLost` — or unparseable) honours
  `invalid_cdc_cursor_position_behavior`: `Fail sync` raises the legacy "Saved offset is not valid…"
  config error for `ChangeStreamHistoryLost` (286) and a "cannot be read by the server … reset the
  connection" one for a token the server cannot parse (9, 260, 280, 40649, 50811), which no oplog
  setting would fix; `Re-sync data` resets the CDC and snapshot state and re-snapshots. Note the server
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
- **Error classification.** `MongoDbExceptionClassifier` (order 5, between the CDK's default
  classifier and the `application.yml` message rules) marks as **transient** — the platform retries
  from the last checkpoint — the failures a retry recovers from: any `MongoSocketException`
  (read/write timeouts, resets), `MongoTimeoutException` (server selection), a cleared connection
  pool, and `MongoCommandException`s with the retryable-reads codes (elections, shutdowns,
  `NotWritablePrimary`, …) plus `CursorNotFound`/`CursorKilled`, and errors carrying the
  `ResumableChangeStreamError` label. The message rules keep the configuration errors
  (authentication, `Unauthorized`, `BSONObjectTooLarge` with the legacy actionable message). CHECK
  needs no special casing: the CDK's `handleCheckFailure` reports every failure as a configuration
  error, so a server-selection timeout is "fix the host" during CHECK and a retry mid-READ.
  `MongoDbExceptionClassifierTest` goes through the CDK's `ExceptionHandler` with real driver
  exceptions — which is how it caught that driver 5.x phrases command errors "Command execution
  failed on MongoDB server with error 13" and the old "Command failed with error 13" rule no
  longer matched.
- **WASS**: an incremental snapshot that exceeds `maxSnapshotReadDuration`
  (`initial_load_timeout_hours`, hidden in the spec like `discover_timeout_seconds`) yields; once
  no stream has anything left to read in this sync, the factory raises a `TransientErrorException`
  (every yielded round is already checkpointed), so the platform retries at once and the retry's
  change-stream read advances the resume token before the snapshots resume — as the JDBC sources
  and the legacy connector do, instead of waiting for the next scheduled sync.
- **Socket / speed mode (protobuf)**: both readers emit through `OutputMessageRouter`, so records go
  over STDIO (JSONL) or the socket data channel (JSONL/PROTOBUF) per `airbyte.connector.data-channel`
  (declared in `metadata.yaml` `connectorIPCOptions.dataChannel`). Because MongoDB is schemaless, each
  value is wrapped in a per-type codec (`MongoDbRecordCodecs.kt`): the JSONL channel takes the value
  as it is, while the protobuf channel coerces it to the field's declared `airbyteSchemaType` — a
  `string` field holding a document or array sends its JSON text — and nulls a value whose actual
  BSON type cannot be coerced (schema/value mismatch is possible on a schemaless store). The payload
  carries every schema field (null for absent) so the protobuf consumer's positional encoding is
  correct.

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
- **Failures mid-read** (`MongoDbSourceFailureInjectionTest`): the replica set runs with
  `--setParameter enableTestCommands=1` and `MongoDbReadTestSupport.withFailPoint` drives MongoDB's
  `failCommand` failpoint, targeted at the connector's client through the `appName` the test
  connection string sets (`withFailingGetMore` drives `failGetMoreAfterCursorCheckout`, a second
  failpoint that combines with it — `failCommand` cannot be reconfigured while a command is held
  in it). A mid-collection checkpoint is produced on demand by `readCutAfter`: the
  `snapshot-batch-size` test hook makes batches of N documents and the `getMore` after the first
  is held past a shortened `checkpoint-target-interval-ms`, so the CDK cancels the round at its
  Nth `_id` and the next round resumes after it — the only way to cut an unbounded cursor, since a
  batch ending on the collection's last document closes the cursor without a final `getMore`.
  Elections (`NotWritablePrimary`, `InterruptedAtShutdown`), a dropped
  cursor and a closed connection mid-snapshot end the sync as a transient error with the previous
  round checkpointed (nothing of the failing round) and the next sync resumes after it; the same mid-change-stream does not
  advance the token; a real `ChangeStreamHistoryLost` (286) honours the invalid-position setting;
  a `find` held on the server lets a test insert *during* the snapshot (observed in `$currentOp`)
  and the next sync replays it above every snapshot row; a `getMore` held past a shortened
  `checkpoint-target-interval-ms` shows the CDK's cancellation checkpointing the last `_id` and the
  next round resuming after it; a `MaxTimeMSExpired` on `$sample` shows discovery keeping its
  partial result. Note the driver retries a failed `aggregate` once (retryable reads): a failpoint
  on it needs `times: 2` to surface.
- **Environments**: `MongoDbSourceVersionMatrixTest` runs a snapshot, a cold start and
  insert/update/delete on MongoDB 4.4, 5.0, 6.0 and 8.0 (7.0 everywhere else), with deletes carrying
  a pre-image on 6.0+ only; `MongoDbSourceShardedClusterTest` uses Testcontainers' single-container
  sharded cluster (`withSharding()`, the collection sharded on a hashed `_id`) for `check`, a
  snapshot read and resumed through `mongos` and the change stream; `MongoDbSourcePermissionsTest` the auth replica
  set above.
- **Catalog and state life cycle** (`MongoDbSourceReadBehaviorsTest`): deselected, absent, wrapped
  and `_aibyte_transform` fields end to end, schemaless incremental syncs, a replace and an update
  storm (one event per update, each looked up at read time), the full-refresh resume/start-over
  contract, a full-refresh-only state starting an incremental sync, an unreadable stream state, a
  collection dropped after discovery (`INCOMPLETE` and the CDK's abort), a failing stream next to
  a completing one, 150 collections, a mixed-type field and a rare field in discovery.
- **Legacy state golden files** (`src/test/resources/legacy-state/`, `MongoDbLegacyStateFixturesTest`):
  the Debezium offset map exactly as `MongoDbDebeziumStateUtil.formatState` wrote it, with the hex
  `_data` token (≤ 2.0.x) and the base64 BSON token produced by Debezium 3.6.2's own
  `ResumeTokens.toBase64` (≥ 2.1.0), plus every legacy stream checkpoint kind.
- `MongoDbClientFactoryTest` pins the client settings (Atlas TLS, connection-string TLS and read
  preference, URL-encoded credentials, the UUID representation pin, honoured string options).

### Remaining work

- **Wire-level socket test:** the protobuf encoding is unit-tested end to end via
  `NativeRecordPayload.toProtobuf`, and the STDIO path is exercised by every read test through
  `OutputMessageRouter`; a full Unix-socket sink test (bind sockets, decode `AirbyteMessageProtobuf`
  frames, compare with STDIO) is still to add. Note the CDK protobuf-consumer fixes land in 1.1.13.
- **Terabyte-scale validation**: bounded-memory, kill/resume and throughput vs the legacy image
  (`airbyte/source-mongodb-v2:2.1.1`) on a very large collection — needs infrastructure not
  available here.

> **CDK version:** `cdkVersion` must be at least `1.1.14`: up to 1.1.13, READ-time catalog
> validation NPE'd on `{"type":"array"}` without `items`, which is how MongoDB arrays are declared
> (`StateManagerFactory.airbyteTypeFromJsonSchema`, fixed in
> [#88342](https://github.com/airbytehq/airbyte/pull/88342)).
