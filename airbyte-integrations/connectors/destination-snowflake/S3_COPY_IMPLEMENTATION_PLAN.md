# Snowflake CSV copies to Airbyte-owned S3

Status: Fusion preview implementation. The exact run layout and temporary routing contract below apply to this preview; broader rollout checks remain planned.

The selected layout is:

```text
s3://airbyte-fusion-context-store/fusion/organizations/<organization_uuid>/workspaces/<workspace_uuid>/sources/<source_uuid>/connections/<connection_uuid>/destinations/<destination_uuid>/syncs/runs/<epoch_seconds>/<run_uuid>/streams/<escaped_original_stream_name>/
  schema.json
  batches/<batch_uuid>.csv.gz
  batches/stream_complete.json
```

Preview writes force enabled `true`, bucket `airbyte-fusion-context-store`, region `us-west-2`, role `arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy`, and prefix `fusion`. The five optional, TEMPORARY top-level advanced config fields are `organization_id`, `workspace_id`, `source_id`, `connection_id`, and `destination_id`. Each nullable string has UUID format: config overrides its matching `AIRBYTE_<NAME>_ID` environment variable, then defaults to `00000000-0000-0000-0000-000000000000`. Supplied values must have the canonical UUID shape; uppercase is normalized, and blank or shortened UUIDs are rejected.

`epoch_seconds` is captured once when the write service/run is created using `Instant.now().epochSecond`, alongside a new run UUID, and passed explicitly to the path helper. All streams and batches in that run reuse it. Stream names preserve original case and use percent-encoded UTF-8 path components. The helper returns the trailing slash; schema, completion, and batch suffixes are appended without another slash. Before uploading sidecars, setup validates every stream path against S3's 1024-byte key limit, including the longest `batches/<batch_uuid>.csv.gz` suffix. Setup writes the run's schema before ingestion; generation IDs remain in metadata rather than directory names. All five IDs, the run UUID, and epoch appear in schema and batch metadata (`epoch_seconds` in JSON, `epoch-seconds` in S3 headers). Consumers resolve `schema.json` in the parent of the batch's `batches` directory.

Repository baseline: `aa28ceeac4e`, reviewed September 9, 2026. Snowflake uses bulk CDK `core = "load"`, `load-csv`, and CDK version `1.0.25`; the checked-in load CDK has the same version.

## 1. Recommendation and delivery contract

Implement this entirely in the Snowflake connector. Upload the existing, closed `.csv.gz` file to Airbyte-owned S3 while the connector performs its existing Snowflake `PUT` followed by `COPY INTO`. Return successfully from the batch's `flush()` only after both operations succeed.

The contract is:

> For an opted-in write, every record processed by that write and covered by an emitted destination checkpoint has its existing Snowflake CSV representation durably stored in S3. After successful stream finalization, a durable `batches/stream_complete.json` identifies the platform job and any requested generation cutoff.

This is an at-least-once archive of load inputs. Completed S3 objects can include records from failed attempts, duplicate records, CDC delete records, and generations that downstream consumers will eventually discard. They are retained. A file's presence does not establish that the sync succeeded or that its records remain in Snowflake's final table.

Make the following choices for v1:

- Force the temporary Fusion preview route in the write-only factory; latch the IDs, epoch, and run UUID for the process lifetime.
- Copy the exact compressed file bytes, with no additional row serialization, recompression, or local spool file.
- Gate existing batch completion on Snowflake and S3. Use the existing CDK checkpoint mechanism.
- Store generation information on each data object and write a stream completion marker with an optional generation cutoff.
- Write one small, versioned schema descriptor per distinct stream layout so the headerless CSV is interpretable.
- Keep completed objects across failures and refreshes. Downstream owns deduplication and deletion semantics.
- Support both Snowflake schema mode and legacy raw-table mode, and both STDIO and socket input paths.

BigQuery, generic CDK shadow accumulators, Iceberg, Glue, table snapshots, backfills, and an end-of-sync publication protocol are outside this change. There is no second S3 commit at the end of the sync: each successful object upload is already the required durable copy.

## 2. Why this fits the current implementation

| Existing code | Relevant behavior and proposed use |
| --- | --- |
| [SnowflakeInsertBuffer.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeInsertBuffer.kt) | Creates a gzip CSV file lazily, closes it in `flush()`, calls Snowflake `PUT` and `COPY INTO`, and deletes the local file in `finally`. Insert the second upload after close; extend file lifetime through both readers. |
| [SnowflakeAggregateFactory.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/dataflow/SnowflakeAggregateFactory.kt) | Has the `DestinationStream`, but currently passes only table/column configuration into the buffer. Pass immutable archive context here. |
| [SnowflakeAggregate.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/dataflow/SnowflakeAggregate.kt) | Delegates to the buffer. No change required to record handling or aggregate semantics. |
| [SnowflakeWriter.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/SnowflakeWriter.kt) | `setup()` precedes data ingestion for the entire catalog. Use it to prepare schemas and generation events, including for empty streams. |
| [SnowflakeColumnManager.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/schema/SnowflakeColumnManager.kt) and [SnowflakeRecordFormatter.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeRecordFormatter.kt) | Define the ordered columns and values. Derive descriptors from these same inputs, including raw-table mode. |
| [SnowflakeDirectLoadSqlGenerator.kt](src/main/kotlin/io/airbyte/integrations/destination/snowflake/sql/SnowflakeDirectLoadSqlGenerator.kt) | Uses gzip input, `AUTO_COMPRESS = FALSE`, and purges Snowflake stage files after copying. Upload the local file directly; do not retrieve it from Snowflake's stage. |

The CDK's [DataFlowPipeline](../../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/DataFlowPipeline.kt) runs the flush stage before the state stage. [StateStage](../../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/StateStage.kt) marks the corresponding counts flushed. [PipelineCompletionHandler](../../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/PipelineCompletionHandler.kt) also calls `Aggregate.flush()` before marking the final partial aggregates flushed. Both paths therefore inherit the S3 requirement from the same buffer change.

This is a shared checkpoint boundary, not an atomic transaction between Snowflake and S3. Snowflake may complete first; S3 may complete first. A failure after either side succeeds leaves partial progress that the normal retry can duplicate.

Also, [PipelineRunner](../../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/PipelineRunner.kt) flushes final states before stream teardown. A batch may load into a temporary Snowflake table that is merged or swapped later. The new guarantee concerns archived load inputs and existing checkpoint semantics; it does not add a guarantee about final table publication.

## 3. Temporary preview configuration contract

`S3CopyConfiguration.fromEnvironment(spec, env)` is a pure parser, separate from Snowflake connection settings. It accepts a supplied environment map so tests can route to mocks. Without the preview overlay it defaults disabled and validates enabled-only fields only for enabled writes. The write-only `SnowflakeBeanFactory` obtains the parsed `injectedSpecification` from the migrating supplier and passes `previewEnvironment(System.getenv())`; only this factory applies the forced preview routing. `@Requires(property = Operation.PROPERTY, value = "write")` gates this before any AWS initialization for `spec` and `check`.

| Setting | Preview behavior |
| --- | --- |
| `AIRBYTE_S3_COPY_ENABLED` | Forced `true` by the preview factory. |
| `AIRBYTE_S3_COPY_BUCKET` | Forced `airbyte-fusion-context-store`. |
| `AIRBYTE_S3_COPY_REGION` | Forced `us-west-2`. |
| `AIRBYTE_S3_COPY_ROLE_ARN` | Forced `arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy`. |
| `AIRBYTE_S3_COPY_PREFIX` | Forced `fusion`; the pure parser normalizes surrounding slashes and rejects an empty prefix. |
| `organization_id`, `workspace_id`, `source_id`, `connection_id`, `destination_id` | Optional TEMPORARY nullable UUID strings in the top-level advanced group of both cloud and OSS specs. |
| `AIRBYTE_ORGANIZATION_ID`, `AIRBYTE_WORKSPACE_ID`, `AIRBYTE_SOURCE_ID`, `AIRBYTE_CONNECTION_ID`, `AIRBYTE_DESTINATION_ID` | Fallbacks for absent/null config fields, then zero UUID. |
| `AIRBYTE_S3_COPY_EXTERNAL_ID` | Optional STS external ID, preserved by the preview overlay. |

Malformed supplied IDs fail enabled writes before ingestion; a valid config value overrides even a malformed environment fallback. No AWS access keys or secret credentials are hardcoded or added to the specification. Existing ambient workload credentials bootstrap AssumeRole. Non-write commands require no archive AWS setup. The temporary fields and forced routing must be revisited before general rollout; the environment enable flag cannot disable this preview factory.

## 4. Credentials, dependencies, and resource ownership

Use AWS SDK for Java v2 directly in the Snowflake connector. Start with a pinned `software.amazon.awssdk:bom:2.46.0`, matching the version already used by [destination-s3-data-lake](../destination-s3-data-lake/build.gradle) at this repository baseline. Include `s3`, `sts`, `netty-nio-client` for async S3, and `url-connection-client` for synchronous STS, with explicit client selection. Check dependency resolution against Snowflake JDBC and Micronaut. Use the standard Java async S3 client, without introducing CRT native dependencies.

Keep `core = "load"` and the current CDK version. Do not add `legacy-task-load-s3`: its [dependency configuration](../../../airbyte-cdk/bulk/toolkits/legacy-task-load-s3/build.gradle) imports the legacy task loader, whose beans conflict with core-load. This feature does not justify migrating the connector or creating a new CDK toolkit.

Credential flow:

```text
Destination workload identity / ambient bootstrap credentials
    -> DefaultCredentialsProvider
    -> regional STS AssumeRole(AIRBYTE_S3_COPY_ROLE_ARN)
    -> refreshing StsAssumeRoleCredentialsProvider
    -> dedicated S3 client
```

The role ARN is not itself a credential. The bootstrap identity must be able to assume the role, and the role must trust that identity. Keep the copy role variable distinct from `AWS_ROLE_ARN`, which may already configure bootstrap web identity. Enable asynchronous credential refresh on the assume-role provider for long syncs rather than resolving temporary credentials once. AWS documents both the [default credential chain](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/credentials-chain.html) and [per-client assume-role providers](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/credentials-providers.html).

Create one credential provider, STS client, and S3 client per enabled write process. Use a role session name containing a generated run UUID. Never assume a role per file or alter global AWS properties that could affect Snowflake JDBC. No static credential fields are added to destination configuration. Deployment must verify that the actual worker environment supplies bootstrap credentials; running on a non-AWS worker does not supply them automatically.

Provision the bucket and role outside the connector. Scope archive access to the assigned prefix. The expected object permissions are `s3:PutObject` and `s3:AbortMultipartUpload`; SSE-KMS additionally needs the appropriate key grants, including `kms:GenerateDataKey` and `kms:Decrypt` for multipart operations. Validate the selected SDK path against this policy. Avoid requiring bucket listing, object reads, or completed-object deletion by using direct writes rather than discovery or read-after-write probes. AWS's [operation-to-permission mapping](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-policy-actions.html) is the authority for the final policy.

Use bucket-controlled encryption and ownership, with no per-object ACL. Configure an incomplete-multipart cleanup lifecycle rule as a fallback for process death; it must not expire completed archive objects as part of refresh handling. AWS recommends [aborting incomplete multipart uploads through lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html).

Resource cleanup needs an explicit owner. The current [DestinationLifecycle](../../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/DestinationLifecycle.kt) does not guarantee `DestinationWriter.teardown()` after failure, and [AirbyteConnectorRunner](../../../airbyte-cdk/bulk/core/base/src/main/kotlin/io/airbyte/cdk/AirbyteConnectorRunner.kt) does not explicitly close its application context before exiting. Give the enabled service an idempotent `close()`: call it from normal writer teardown, register a JVM shutdown fallback, and expose it to test cleanup. A Micronaut destruction hook can also call it, but must not be the only cleanup mechanism. Close owned clients/providers/executors and remove the shutdown hook after normal close.

## 5. S3 object contract

### Identity and layout

Use original stream identity for archive routing. The buffer's execution table may be temporary and must not become the archive's stream identity.

```text
s3://airbyte-fusion-context-store/fusion/organizations/<organization_uuid>/workspaces/<workspace_uuid>/sources/<source_uuid>/connections/<connection_uuid>/destinations/<destination_uuid>/syncs/runs/<epoch_seconds>/<run_uuid>/streams/<escaped_original_stream_name>/
  schema.json
  batches/<batch_uuid>.csv.gz
  batches/stream_complete.json
```

- `stream_key`: SHA-256 of a canonical JSON object containing the unmapped namespace and name. Preserve the distinction between a null and empty namespace. Store the readable original and mapped identities in the schema/event JSON.
- `epoch_seconds`: captured once at run creation, shared by all streams, sidecars, and batch headers.
- `run_uuid`: generated once per connector write process. Catalog `syncId` is also recorded, but is not relied on for attempt uniqueness.
- `batch_uuid`: generated once per closed CSV file, before beginning the upload. Reuse the same key and metadata for SDK retries of that upload.
- `schema_id`: SHA-256 of the canonical descriptor body, excluding the ID itself. Preserve column-array order when canonicalizing.

New process attempts can create new objects containing repeated records. Do not hash data files to deduplicate them, derive keys solely from generation or table name, or use one overwriteable object per generation. Generation comparisons are scoped to a connection and stream, never global.

### Data objects

Upload the local file unchanged as `application/gzip`, with no `Content-Encoding` header. The descriptor identifies its contents as gzip-compressed CSV; consumers explicitly decompress the archive file. This avoids depending on HTTP clients' automatic content decoding.

Set the following user metadata on the upload request. Values are short ASCII strings; names below are SDK map keys, without the HTTP `x-amz-meta-` prefix:

```json
{
  "format-version": "1",
  "organization-id": "00000000-0000-0000-0000-000000000001",
  "workspace-id": "00000000-0000-0000-0000-000000000002",
  "source-id": "00000000-0000-0000-0000-000000000003",
  "connection-id": "00000000-0000-0000-0000-000000000004",
  "destination-id": "00000000-0000-0000-0000-000000000005",
  "epoch-seconds": "1789400000",
  "stream-key": "<sha256>",
  "generation-id": "42",
  "sync-id": "12345",
  "run-id": "<uuid>",
  "batch-id": "<uuid>",
  "schema-id": "<sha256>",
  "record-count": "10000"
}
```

Use the buffer's existing record count and the file's compressed size for metrics; do not scan the file for these. The CDK supplies stream generation IDs to records in both input paths; test that the object metadata matches the CSV generation column. No per-record generation inspection is needed in the archive integration.

S3 user metadata has a 2 KB limit and lowercase keys. Keep column lists, Unicode names, and rich schema information in the descriptor instead of headers. [S3 object metadata documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html).

### Schema descriptors

Write descriptors as `application/json` before ingesting data. Their successful upload is a prerequisite for returning successfully from writer setup. Each stream has its own `schema.json` in each run; schema IDs still hash the descriptor body independently of run identity. No `HEAD` request or read permission is necessary.

Every descriptor includes top-level `source_schema`, in both raw and typed modes. It preserves the matching configured stream's original JSON Schema, including nested field types and annotations, independently of the physical CSV `columns`. If no configured schema is supplied, reconstruct it from the CDK's retained input schema. The source schema participates in `schema_id`; raw mode's `_airbyte_data` storage layout must never replace it.

The descriptor contains:

- All five routing UUIDs, run UUID, epoch seconds, generation and sync IDs, and the schema ID.
- Contract version, connector name/version, and format identifier `snowflake-load-csv-gzip-v1`.
- Original and mapped stream descriptors, and the logical final Snowflake database/schema/table. Exclude temporary table names from stable identity.
- Mode: schema columns or legacy raw table.
- Ordered column names, Snowflake types, and nullability, drawn from `getTableColumnNames()`, `getMetaColumns()`, and `columnSchema.finalSchema`. Include the input-to-final name mapping for schema mode.
- Writer dialect: encoding, comma separator, double-quote enclosure, LF record separator, no header, and gzip compression. Confirm the existing FastCSV encoding in a fixture; describe the existing bytes without changing the writer.
- The relevant explicit `COPY` file-format options, especially `TRIM_SPACE`. Record unspecified options as inherited Snowflake defaults rather than inventing values. The descriptor describes load inputs; it does not promise to reproduce all server-side conversion semantics.

Keep the explicit COPY options and descriptor in agreement through a focused test, or a small connector-local value object if that is simpler. Do not duplicate a hardcoded standard-mode column list: legacy mode has `_airbyte_loaded_at` and a JSON `_airbyte_data` column.

The CSV already reflects Airbyte's mapping, coercion, and formatting. Null/missing values and empty fields follow the current formatter; nested values are serialized by that formatter. This archive cannot recover source fields already discarded before the buffer or distinctions already lost in CSV formatting. CDC fields that reach the CSV are copied as ordinary fields.

The schema includes `primary_key` (a list of source field paths) and `cursor` (a source field
path), sourced from the original configured catalog so append-mode keys/cursors survive.
Absent keys/cursors are explicit empty arrays. These fields participate in the schema hash.

### Stream completion

After the final batch archive is durable and the stream's successful Snowflake teardown returns,
write `batches/stream_complete.json` once, including for empty streams:

```json
{"job_id": 12345, "min_generation_id": 42}
```

`job_id` is the platform job ID supplied as the configured catalog stream's `syncId`, not the
random run UUID or attempt ID. Omit `min_generation_id` entirely when `minimumGenerationId` is
zero. The numeric cutoff is included only when positive. Keep the existing hybrid refresh
validation (minimum zero or equal to current generation).

Schema is written during setup; no `generation-cutoff.json` or `truncate_refresh.json` is emitted.
Failed/incomplete streams and failed destination finalization do not emit completion. Marker
upload failure propagates as a sync failure, and retries use the same key and payload. Successful
markers are retained if another stream or the overall job later fails. The marker signals a
completed stream, not a successful platform job: consumers wait for that job to succeed and for
replacement batches to finish indexing before applying generation cleanup. The `batches/`
location ensures the marker is delivered to the same event listeners as data objects.

## 6. Implementation structure and execution

Add a small connector-local `copy` package:

| Proposed component | Responsibility |
| --- | --- |
| `S3CopyConfiguration` / `S3CopyBeanFactory` | Operation/flag selection, enabled-only validation, credential and client construction. |
| `SnowflakeS3Copy` with disabled and enabled implementations | `prepare(catalog)`, immutable stream context lookup, upload of a closed CSV, and idempotent resource close. This is the integration seam used by tests. |
| `CsvCopyContext` / batch metadata | Connection, stream, generation, sync, run, schema reference, and per-file identity. No mutable global "current stream". |
| `S3CopyMetadata` | Versioned descriptor/event serialization and canonical key derivation. |
| `S3CsvUploader` | Bounded file uploads, request metadata, retry/timeout policy, and completion/file-reader lifetime. |

These are responsibilities, not a requirement to create one file per row. Keep the public surface small; do not introduce a general storage abstraction or a second batching system.

### Startup

1. On enabled writes, validate internal configuration and supported generation combinations for the whole catalog.
2. Run existing Snowflake setup. Before `setup()` returns, call `SnowflakeS3Copy.prepare(catalog)` and await all required descriptor writes. Cap metadata request concurrency as well as data uploads.
3. Build an immutable context for every stream. Schema descriptors come from the same catalog column schema that the aggregate factory will pass into the buffer.
4. Begin the existing stream initialization and ingestion lifecycle. There is no per-row archive work.

No separate bucket-listing or write-and-delete access probe is needed: the required metadata writes exercise actual access. If the catalog is empty, resolve the assumed-role credentials but create no synthetic data object; there is no stream data or completion to publish.

### Batch flush

In `SnowflakeAggregateFactory.create()`, pass the copy service and the stream's context to the buffer. Retain the existing no-op behavior when disabled.

The enabled flush performs:

```text
close CSV writer, including the gzip footer
capture file path, record count, column order, and batch UUID
acquire a bounded copy slot

start two supervised operations:
    Snowflake: PUT existing local file -> COPY INTO using existing column order
    S3:        upload the same existing local file, including object metadata

wait for both operations to settle
if either failed or the parent was cancelled: propagate failure
otherwise: return success to the CDK

cleanup: release upload slot and delete local file only after readers stop
```

Snowflake `PUT` and `COPY` remain sequential within their branch. Run blocking JDBC work on an appropriate IO dispatcher. Use structured concurrency, with ordinary failures captured as branch outcomes so an early failure does not abandon the other branch or its file reader. Preserve both causes when both branches fail; preserve cancellation as cancellation.

S3 success means the final object operation has succeeded, including multipart completion. Finishing an individual part, scheduling a future, or flushing an output stream is insufficient. The standard Java S3 async client supports [automatic multipart uploads](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/s3-async-client-multipart.html); use it with a file-backed request body instead of loading the file into a byte array.

File ownership is a release criterion, not just a cleanup detail. Coroutine or future cancellation does not by itself prove the SDK has stopped reading the path. The uploader must track terminal transfer/reader completion and let the flush drain both readers before ordinary deletion. On cancellation, cancel/abort where supported and perform bounded cleanup. If reader shutdown cannot be established, retain the temporary file for process/container cleanup rather than unlinking a file still needed by an active operation. Never turn this cleanup fallback into successful batch completion.

On an ordinary S3 failure, let an already-started Snowflake operation settle and fail the composite flush; on a Snowflake failure, likewise settle the S3 branch and retain any object that completed. Apply finite SDK request retries to the same immutable key/file. Do not retry the entire composite flush inside the connector after Snowflake may have succeeded. Source replay through the normal platform retry is the existing at-least-once mechanism.

### Bounds and overhead

Start with at most four concurrent file copies per connector process, a global S3 HTTP concurrency cap of 16, a 64 MiB multipart threshold, and 16 MiB minimum parts. These are internal implementation defaults to verify in the pilot, not new user settings. Let the SDK handle valid part sizing for larger files.

Acquire the copy slot before starting the paired batch operations. This bounds retained in-flight files and makes a slow S3 sink apply backpressure through the existing flush pipeline. Do not change the connector's aggregate thresholds in the initial change: it currently targets about 350 MB of estimated input per aggregate, not an exact compressed file size.

Use finite standard SDK retries and explicit network deadlines. Initial budgets: three total attempts per request, 10-second connection timeout, 2-minute request-attempt timeout, and a 30-minute total file-transfer deadline. Verify that the whole-transfer deadline actually covers multipart orchestration, and that timeout cancellation follows the file-lifetime rule above. Keep existing Snowflake timeout behavior. These budgets are starting values for representative load tests, not a throughput guarantee.

Enabled overhead is an additional read of the compressed file, S3 network traffic, SDK transfer buffers, and small metadata writes. Parallel operation makes the upload portion approximately bounded by the slower of S3 and Snowflake when resources are available, but shared disk/network contention can still slow Snowflake. There is no additional row parsing, serialization, compression, full-file hash pass, or second local file. Disabled writes must avoid all of that work and AWS initialization.

## 7. Failure and retry behavior

| Outcome | State/checkpoint behavior | S3 disposition |
| --- | --- | --- |
| Descriptor write fails during setup | Fail before ingesting records. | Retain any metadata already written. |
| Snowflake succeeds; S3 succeeds | Batch becomes eligible for existing CDK state reconciliation. | Retain the complete object. |
| Snowflake succeeds; S3 fails | Fail the batch; do not advance state through its records. | Retain any complete object if the response was ambiguous; abort incomplete upload where possible. |
| S3 succeeds; Snowflake fails | Fail the batch; do not advance state through its records. | Retain the complete object. |
| Both succeed; process dies before checkpoint emission | Normal replay may repeat the records. | Retain all complete objects from both attempts. |
| Process dies during upload | No success from that flush. | Incomplete multipart lifecycle handles abandoned parts. |
| Final Snowflake merge/swap fails after earlier checkpoints | Existing CDK retry semantics apply. | Keep all completed copies; completed stream markers remain tied to the platform job outcome. |
| Refresh or CDC delete arrives | Existing Snowflake behavior applies. | Record the directive/event or existing CSV row; perform no archive deletion. |

Earlier independent checkpoints can still be emitted if all their records satisfy the contract. The guarantee is that a failing or unfinished copy never contributes flushed counts for its batch, not that every checkpoint in every stream stops immediately on the first error.

Do not clean an S3 run prefix when a sync fails. Some objects in that prefix can contain records already checkpointed, which the next attempt will not replay.

## 8. Tests that establish the contract

### Deterministic connector tests

Extend [SnowflakeInsertBufferTest](src/test/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeInsertBufferTest.kt), the aggregate factory tests, and writer tests. Use controlled deferred completions/latches rather than sleeps.

1. **Byte identity:** capture bytes read by Snowflake `PUT` and by the fake S3 uploader; assert equality and a valid completed gzip stream. Cover quoted delimiters/newlines, Unicode, empty/null fields, numbers/timestamps, nested JSON, and Airbyte metadata.
2. **Both completion orders:** hold S3 after Snowflake succeeds, then reverse the order. `flush()` must remain incomplete until both succeed.
3. **Failure and cancellation:** independently fail `PUT`, `COPY`, S3 upload, multipart completion, and cancellation. Assert failure propagation, no premature file deletion, and release of slots/resources. Include an uploader whose future is cancelled before its reader terminates.
4. **Retry identity:** an SDK-level retry uses the same key and file; a new process/batch gets a distinct key. S3 failure must not cause an extra connector-issued Snowflake `COPY`.
5. **Metadata:** verify generation, sync ID, row count, stable stream identity, column order/types, source-to-final mapping, and both schema/raw modes. Separate null namespace from empty namespace; exercise renamed columns and temporary execution tables.
6. **Control events:** minimum zero emits none; supported nonzero minimum emits the strict-less-than directive, including zero-row streams. A metadata write failure fails setup. Repeated attempts produce replayable events. Unsupported hybrid generations preserve current errors.
7. **Disabled/other operations:** no AWS bean construction, credential discovery, network calls, or additional files for disabled writes, `check`, and `spec`, including missing enabled-only settings. Enabled misconfiguration fails before data ingestion.

### Checkpoint integration test

Add a connector test that runs the real core-load pipeline with a controlled S3 service and a fake Snowflake client. Feed records and state messages, then block the copy. Assert that destination state covering those records is absent while S3 is pending and emitted only after both writes finish. Repeat with the Snowflake branch pending and each branch failing.

Exercise an ordinary aggregate flush, the final partial aggregate at EOF, and multiple streams/partitions with global state. Verify the zero-row refresh case separately. This is the critical proof: a buffer mock test alone does not establish checkpoint behavior.

### Real service and performance validation

- In an AWS test bucket and Snowflake test account, run append, dedup, refresh, schema evolution, and legacy raw-table scenarios. Compare uploaded bytes with the original file captured by the fixture and validate Snowflake results through the existing acceptance utilities.
- Force multipart with a lowered test threshold, inject a mid-transfer failure, and verify completion/abort behavior. Exercise a file above the single-request upload limit in a targeted SDK test or pre-rollout job.
- Test real STS trust/external-ID failures, prefix denial, and a run spanning credential refresh. Use separate reader credentials in the test harness if it needs to inspect objects; do not widen the production writer role for test convenience.
- Run STDIO and socket ingestion through the feature. Compare representative throughput, CPU, heap, retained temporary bytes, and checkpoint latency with copying disabled/enabled. Verify that buffers and upload slots stay bounded when S3 is throttled.
- Re-run the existing Snowflake unit suite and relevant acceptance/spec checks. Cloud and OSS spec snapshots include the five optional temporary UUID fields; central tests should compare them with the actual generated specification.

Implementation validation commands, from the repository root:

```sh
./gradlew :airbyte-integrations:connectors:destination-snowflake:test
./gradlew :airbyte-integrations:connectors:destination-snowflake:integrationTestNonDocker
```

The second command requires configured service test resources; the repository's Docker-oriented CI task is `integrationTestJava`. These are planned implementation checks, not tests run for this document.

## 9. Delivery sequence and rollout

### Change 1: internal configuration and AWS uploader

Add the gated configuration/factory, minimal AWS dependencies in [build.gradle.kts](build.gradle.kts), resource ownership, and file uploader. Add deterministic uploader/configuration tests. Use dedicated internal Micronaut properties or [application-connector.yml](src/main/resources/application-connector.yml) bindings without eagerly validating disabled settings. Keep preview routing isolated to the write factory; retain the pure parser for mock routing.

Deliverable: an independently testable service that uploads an existing file under the assumed role and returns only on terminal success, with bounded resource use.

### Change 2: metadata and lifecycle integration

Add versioned descriptors, stable keys, generation events, and immutable stream contexts. Wire preparation into `SnowflakeWriter.setup()` and normal resource close into teardown. Refactor the existing generation validation into a small shared helper if needed so startup and stream-loader selection cannot disagree. Pass context from `SnowflakeAggregateFactory`.

Deliverable: every enabled stream has durable interpretation metadata and a completion marker after successful finalization, including empty streams.

### Change 3: paired flush and checkpoint proof

Modify `SnowflakeInsertBuffer.flush()` to run the two writes against the closed file and gate success on both. Add byte-identity, cancellation, lifetime, failure-matrix, and actual pipeline checkpoint tests. Keep the record formatter, row accumulation loop, and CDK state logic unchanged.

Deliverable: the stated data/checkpoint contract is enforced on both regular and EOF flush paths. Changes 1–3 may be separate review commits, but do not enable the feature before all three land.

### Change 4: deployment and pilot

Provision the Airbyte-owned bucket, scoped role/trust, encryption, and incomplete-upload lifecycle. Wire environment injection with connector-version gating and stable opt-in across attempts. Verify bootstrap identity in each worker environment intended for the pilot. The preview forces enablement; restore an explicit rollout control before general availability.

Log one startup event identifying copy enablement and the archive contract version. Add counters for files/bytes/records successfully copied, failures by operation, retries, and metadata events; add timers for copy duration, waiting for a copy slot, and extra flush wait after Snowflake succeeds. Use existing connector metrics/logging facilities. Keep connection/run/batch identifiers in structured diagnostic logs instead of high-cardinality metric labels. Do not log payloads, credential material, or full configuration.

Run failure injection before expanding enablement. A slow or unavailable S3 service should visibly delay/fail opted-in writes. The preview overlay overrides the enable flag, so disabling requires a code/deployment change; do not automatically disable after an upload failure. No rollback deletes archive data.

## 10. Acceptance criteria and remaining deployment inputs

The implementation is complete when:

- The exact existing `.csv.gz` bytes are archived for all checkpointed batches in enabled writes, in both input paths and Snowflake output modes.
- No batch contributes flushed state until both Snowflake and S3 succeed, including the final partial batch.
- Descriptors are durable before ingestion. Stream completion markers are durable before successful stream teardown returns, including streams with no rows.
- Failures propagate, retries remain at least once, and completed S3 data survives failed attempts and refreshes.
- Long-running writes refresh credentials; cancellation and timeouts do not delete files still in use or leak unbounded transfers.
- The pure parser supports disabled writes without AWS setup. Non-write commands do not initialize archive AWS clients; the public specification exposes only the five optional temporary routing fields.
- Real-service tests establish role access, multipart behavior, and acceptable resource use before rollout.

The preview bucket, region, prefix, and role are fixed above. The coordinator reported provisioning the private AES256 bucket, one-day incomplete-upload lifecycle, prefix-scoped role policy, and successful real AssumeRole/Put verification. Central build, generated-spec validation, and runtime tests remain coordinator-owned. Platform ID injection and worker bootstrap identity remain rollout concerns. No format conversion, Iceberg dependency, or generic CDK implementation is needed to deliver this contract.
