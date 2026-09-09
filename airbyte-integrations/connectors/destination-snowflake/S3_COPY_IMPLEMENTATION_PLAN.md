# Snowflake CSV copies to Airbyte-owned S3

Status: implementation in progress. The run layout below supersedes the original content-addressed schema location and generation directory described later in this plan.

The selected layout is:

```text
fusion/workspaces/<workspace_uuid>/sources/<source_uuid>/connections/<connection_uuid>/streams/<escaped_original_stream_name>/runs/<run_uuid>/
  schema.json
  generation-cutoff.json  # only when a cutoff is requested
  batches/<batch_uuid>.csv.gz
```

`AIRBYTE_S3_COPY_WORKSPACE_ID` and `AIRBYTE_S3_COPY_CONNECTION_ID` are required UUIDs for enabled writes. `AIRBYTE_S3_COPY_PREFIX` defaults to `fusion`. Stream names preserve case and use percent-encoded UTF-8 path components. Setup writes the run's schema and any cutoff before ingestion; generation IDs remain in metadata rather than directory names. Schema IDs remain layout references in both schema JSON and batch metadata. Consumers resolve `schema.json` in the parent of the batch's `batches` directory.

Repository baseline: `aa28ceeac4e`, reviewed September 9, 2026. Snowflake uses bulk CDK `core = "load"`, `load-csv`, and CDK version `1.0.25`; the checked-in load CDK has the same version.

## 1. Recommendation and delivery contract

Implement this entirely in the Snowflake connector. Upload the existing, closed `.csv.gz` file to Airbyte-owned S3 while the connector performs its existing Snowflake `PUT` followed by `COPY INTO`. Return successfully from the batch's `flush()` only after both operations succeed.

The contract is:

> For an opted-in write, every record processed by that write and covered by an emitted destination checkpoint has its existing Snowflake CSV representation durably stored in S3. Any generation-cutoff directive supplied for that stream has also been recorded in S3.

This is an at-least-once archive of load inputs. Completed S3 objects can include records from failed attempts, duplicate records, CDC delete records, and generations that downstream consumers will eventually discard. They are retained. A file's presence does not establish that the sync succeeded or that its records remain in Snowflake's final table.

Make the following choices for v1:

- Enable through internal destination environment variables, latched for the lifetime of the write process. Default off.
- Copy the exact compressed file bytes, with no additional row serialization, recompression, or local spool file.
- Gate existing batch completion on Snowflake and S3. Use the existing CDK checkpoint mechanism.
- Store generation information on each data object and write separate JSON generation-cutoff events.
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

## 3. Internal environment contract

Use a dedicated `S3CopyConfiguration`, separate from `SnowflakeConfiguration` and the connector specification. Read it through a Micronaut factory that checks the operation and enablement flag before binding or validating enabled-only fields. The factory must return a no-op implementation for non-write operations and disabled writes without initializing AWS clients or discovering credentials.

Proposed variables:

| Variable | Requirement | Meaning |
| --- | --- | --- |
| `AIRBYTE_S3_COPY_ENABLED` | Defaults to `false` | Accept explicit `true` or `false`; reject other values for `write`. |
| `AIRBYTE_S3_COPY_ROLE_ARN` | Required when enabled | Target IAM role assumed by this connector for archive writes. |
| `AIRBYTE_S3_COPY_BUCKET` | Required when enabled | Airbyte-owned bucket name. |
| `AIRBYTE_S3_COPY_REGION` | Required when enabled | Bucket region; configure the S3 client and a regional STS endpoint explicitly. |
| `AIRBYTE_S3_COPY_CONNECTION_ID` | Required when enabled | Stable Airbyte connection UUID, unchanged across attempts and syncs. |
| `AIRBYTE_S3_COPY_PREFIX` | Defaults to `snowflake-copy/v1` | Deployment-controlled root prefix. Normalize surrounding slashes and reject an empty root. |
| `AIRBYTE_S3_COPY_EXTERNAL_ID` | Optional | STS external ID, if required by the target role's trust policy. |

The flag and role are sufficient to express opt-in and authorization intent, but they do not identify the bucket, region, or connection. Supply those additional routing values through environment variables as well. Keep them as deployment settings; they do not enter the user-facing connector spec. Existing job ID and attempt environment variables may be added to diagnostic metadata if available, but correctness must not depend on them.

Rules:

1. `spec` and `check` ignore this feature even if the flag is set. They must neither contact AWS nor fail because archive configuration is missing.
2. A disabled write ignores enabled-only configuration, including malformed values. The existing write behavior remains available without any AWS setup.
3. An enabled write validates the complete configuration before ingesting records. A missing role, invalid connection ID, credential failure, or denied upload fails the write. It never silently disables copying.
4. Report archive failures as internal destination failures, identifying the failing operation. Do not describe an Airbyte-owned role or bucket error as invalid customer Snowflake credentials.
5. Do not change the environment or feature decision during an active write. Platform retries of an opted-in sync must retain the same decision and routing.

The platform work is a small but required companion: inject these values into the destination container, provide its bootstrap identity, and gate enablement on connector versions that implement the contract. An older image can ignore unknown environment variables, so setting the flag alone is not evidence that copying occurred.

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
<prefix>/connections/<connection_uuid>/streams/<stream_key>/
  schemas/<schema_id>.json
  generations/<generation_id>/runs/<run_uuid>/batches/<batch_uuid>.csv.gz
  events/<run_uuid>/generation-cutoff.json
```

- `stream_key`: SHA-256 of a canonical JSON object containing the unmapped namespace and name. Preserve the distinction between a null and empty namespace. Store the readable original and mapped identities in the schema/event JSON.
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
  "connection-id": "00000000-0000-0000-0000-000000000001",
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

Write descriptors as `application/json` before ingesting data. Their successful upload is a prerequisite for returning successfully from writer setup. Rewriting a content-addressed descriptor on a later run is acceptable because its bytes are identical; no `HEAD` request or read permission is necessary.

The descriptor contains:

- Contract version, connector name/version, and format identifier `snowflake-load-csv-gzip-v1`.
- Original and mapped stream descriptors, and the logical final Snowflake database/schema/table. Exclude temporary table names from stable identity.
- Mode: schema columns or legacy raw table.
- Ordered column names, Snowflake types, and nullability, drawn from `getTableColumnNames()`, `getMetaColumns()`, and `columnSchema.finalSchema`. Include the input-to-final name mapping for schema mode.
- Writer dialect: encoding, comma separator, double-quote enclosure, LF record separator, no header, and gzip compression. Confirm the existing FastCSV encoding in a fixture; describe the existing bytes without changing the writer.
- The relevant explicit `COPY` file-format options, especially `TRIM_SPACE`. Record unspecified options as inherited Snowflake defaults rather than inventing values. The descriptor describes load inputs; it does not promise to reproduce all server-side conversion semantics.

Keep the explicit COPY options and descriptor in agreement through a focused test, or a small connector-local value object if that is simpler. Do not duplicate a hardcoded standard-mode column list: legacy mode has `_airbyte_loaded_at` and a JSON `_airbyte_data` column.

The CSV already reflects Airbyte's mapping, coercion, and formatting. Null/missing values and empty fields follow the current formatter; nested values are serialized by that formatter. This archive cannot recover source fields already discarded before the buffer or distinctions already lost in CSV formatting. CDC fields that reach the CSV are copied as ordinary fields.

### Generation-cutoff events

For a supported stream with `minimumGenerationId > 0`, write one event per run before the data pipeline starts. Example:

```json
{
  "format_version": 1,
  "event_type": "generation_cutoff_requested",
  "event_id": "<uuid>",
  "connection_id": "00000000-0000-0000-0000-000000000001",
  "stream_key": "<sha256>",
  "stream": {"namespace": "public", "name": "orders"},
  "mapped_stream": {"namespace": "analytics", "name": "orders"},
  "generation_id": 42,
  "minimum_generation_id": 42,
  "sync_id": 12345,
  "run_id": "<uuid>",
  "requested_effect": "discard_records_with_generation_id_less_than_minimum"
}
```

Generate the event once and reuse its bytes on request retries. Duplicate events across process attempts are allowed. The cutoff is strictly `< minimum_generation_id`.

Emit from the catalog's directive, not from seeing a new generation number. A new generation with minimum zero does not request discarding older generations. Validate the same generation combinations Snowflake currently supports: minimum zero or minimum equal to current generation. Preserve the existing failure for unsupported hybrid refreshes; do not independently invent broader refresh support.

Name the event `requested` deliberately: writer setup precedes Snowflake's eventual truncate/swap. The event records the instruction even if the sync later fails. Downstream must not interpret it as proof that the final Snowflake table was refreshed successfully. This satisfies the requirement to retain the fact of a delete directive. A future consumer requiring successful-refresh evidence would need an additional completion contract.

Write the event for zero-row streams too. Its upload failure fails setup, preventing even an empty-stream checkpoint from passing before the directive is durable. Do not issue S3 deletes, rewrite previous data files, or emit record-level tombstones by parsing the CSV.

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
2. Run existing Snowflake setup. Before `setup()` returns, call `SnowflakeS3Copy.prepare(catalog)` and await all required descriptor and cutoff writes. Cap metadata request concurrency as well as data uploads.
3. Build an immutable context for every stream. Schema descriptors come from the same catalog column schema that the aggregate factory will pass into the buffer.
4. Begin the existing stream initialization and ingestion lifecycle. There is no per-row archive work.

No separate bucket-listing or write-and-delete access probe is needed: the required metadata writes exercise actual access. If the catalog is empty, resolve the assumed-role credentials but create no synthetic data object; there is no stream data or cutoff to protect.

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
| Descriptor or cutoff write fails during setup | Fail before ingesting records. | Retain any metadata already written. |
| Snowflake succeeds; S3 succeeds | Batch becomes eligible for existing CDK state reconciliation. | Retain the complete object. |
| Snowflake succeeds; S3 fails | Fail the batch; do not advance state through its records. | Retain any complete object if the response was ambiguous; abort incomplete upload where possible. |
| S3 succeeds; Snowflake fails | Fail the batch; do not advance state through its records. | Retain the complete object. |
| Both succeed; process dies before checkpoint emission | Normal replay may repeat the records. | Retain all complete objects from both attempts. |
| Process dies during upload | No success from that flush. | Incomplete multipart lifecycle handles abandoned parts. |
| Final Snowflake merge/swap fails after earlier checkpoints | Existing CDK retry semantics apply. | Keep all completed copies; cutoff event remains a requested directive. |
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
- Re-run the existing Snowflake unit suite and relevant acceptance/spec checks. Expected cloud and OSS specs should be identical to their existing snapshots.

Implementation validation commands, from the repository root:

```sh
./gradlew :airbyte-integrations:connectors:destination-snowflake:test
./gradlew :airbyte-integrations:connectors:destination-snowflake:integrationTestNonDocker
```

The second command requires configured service test resources; the repository's Docker-oriented CI task is `integrationTestJava`. These are planned implementation checks, not tests run for this document.

## 9. Delivery sequence and rollout

### Change 1: internal configuration and AWS uploader

Add the gated configuration/factory, minimal AWS dependencies in [build.gradle.kts](build.gradle.kts), resource ownership, and file uploader. Add deterministic uploader/configuration tests. Use dedicated internal Micronaut properties or [application-connector.yml](src/main/resources/application-connector.yml) bindings without eagerly validating disabled settings. Keep the feature default off.

Deliverable: an independently testable service that uploads an existing file under the assumed role and returns only on terminal success, with bounded resource use.

### Change 2: metadata and lifecycle integration

Add versioned descriptors, stable keys, generation events, and immutable stream contexts. Wire preparation into `SnowflakeWriter.setup()` and normal resource close into teardown. Refactor the existing generation validation into a small shared helper if needed so startup and stream-loader selection cannot disagree. Pass context from `SnowflakeAggregateFactory`.

Deliverable: every enabled stream has durable interpretation metadata and any cutoff event before ingestion starts, including empty streams.

### Change 3: paired flush and checkpoint proof

Modify `SnowflakeInsertBuffer.flush()` to run the two writes against the closed file and gate success on both. Add byte-identity, cancellation, lifetime, failure-matrix, and actual pipeline checkpoint tests. Keep the record formatter, row accumulation loop, and CDK state logic unchanged.

Deliverable: the stated data/checkpoint contract is enforced on both regular and EOF flush paths. Changes 1–3 may be separate review commits, but do not enable the feature before all three land.

### Change 4: deployment and pilot

Provision the Airbyte-owned bucket, scoped role/trust, encryption, and incomplete-upload lifecycle. Wire environment injection with connector-version gating and stable opt-in across attempts. Verify bootstrap identity in each worker environment intended for the pilot. Select the first opted-in connections internally; retain the flag as the rollout control.

Log one startup event identifying copy enablement and the archive contract version. Add counters for files/bytes/records successfully copied, failures by operation, retries, and metadata events; add timers for copy duration, waiting for a copy slot, and extra flush wait after Snowflake succeeds. Use existing connector metrics/logging facilities. Keep connection/run/batch identifiers in structured diagnostic logs instead of high-cardinality metric labels. Do not log payloads, credential material, or full configuration.

Run failure injection before expanding enablement. A slow or unavailable S3 service should visibly delay/fail opted-in writes. Disabling the flag applies to future attempts/syncs and creates a deliberate archive coverage gap; it must not become an automatic response to an upload failure. No rollback deletes archive data.

## 10. Acceptance criteria and remaining deployment inputs

The implementation is complete when:

- The exact existing `.csv.gz` bytes are archived for all checkpointed batches in enabled writes, in both input paths and Snowflake output modes.
- No batch contributes flushed state until both Snowflake and S3 succeed, including the final partial batch.
- Descriptors and requested generation cutoffs are durable before relevant state can be emitted, including streams with no rows.
- Failures propagate, retries remain at least once, and completed S3 data survives failed attempts and refreshes.
- Long-running writes refresh credentials; cancellation and timeouts do not delete files still in use or leak unbounded transfers.
- Disabled writes and non-write commands require no AWS setup and preserve the public specification.
- Real-service tests establish role access, multipart behavior, and acceptable resource use before rollout.

The remaining inputs are deployment values, not connector design blockers: bucket/region/prefix, the connection-ID injection source, target role and optional external ID, and the bootstrap identity available to the destination workload. Confirm those before the first enabled deployment. No format conversion, Iceberg dependency, or generic CDK implementation is needed to deliver this contract.
