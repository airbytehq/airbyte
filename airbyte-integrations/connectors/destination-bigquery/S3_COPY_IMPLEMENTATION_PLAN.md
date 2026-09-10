# BigQuery load-input copies for Fusion

Status: implemented for GCS staging on `johnny/bigquery-fusion-sync-copy`; standard inserts remain
unsupported when copying is enabled. Copying defaults off. No deployment-specific settings or
credentials are embedded in the connector. The sections below describe the implementation contract
and rollout requirements.
Reviewed September 10, 2026 against the BigQuery files at repository baseline `aa28ceeac4e`.
The connector uses CDK `1.0.25`, `core = 'load'`, and `useLegacyTaskLoader = true`, with
`legacy-task-load-gcs`, `legacy-task-load-db`, and `legacy-task-load-s3` toolkits.

## 1. Start with GCS staging

Implement the **GCS staging load strategy first**, in both schema-table and legacy raw-table modes,
and with both STDIO and socket ingestion. Keep batched standard inserts outside v1.

| Strategy | Existing load representation | Archive work | Decision |
| --- | --- | --- | --- |
| GCS staging | Completed gzip CSV object, including a header, supplied to a BigQuery load job | Read the completed object, upload the same bytes to S3, delay completion and GCS deletion | First: one connector-local load hook covers both input paths |
| Batched standard inserts | UTF-8 NDJSON, buffered initially and then streamed into `TableDataWriteChannel` | Capture every formatted byte before it is discarded, introduce spool ownership and an NDJSON contract, gate `finish()` | Later: more changes to byte production and lifetime |

Evidence: [BigQueryBulkLoader.kt](src/main/kotlin/io/airbyte/integrations/destination/bigquery/write/bulk_loader/BigQueryBulkLoader.kt)
accepts a completed `GcsBlob`, submits a CSV load job, waits for completion, checks bad records,
and optionally deletes the blob. Both ingestion paths call this loader. By contrast,
[BigqueryBatchStandardInsertLoader.kt](src/main/kotlin/io/airbyte/integrations/destination/bigquery/write/standard_insert/BigqueryBatchStandardInsertLoader.kt)
formats NDJSON in `accept()`, initially uses a byte-array buffer, and switches to a write channel
above 15 MiB. It has no reusable completed file. Its name does not mean it uses the streaming
`insertAll` API; it closes a write channel and waits for a load job in `finish()`.

For the smallest first change, use **sequential completion**:
BigQuery job success → archive completed GCS object → existing GCS post-processing → return.
This adds transfer latency after the BigQuery job, but avoids simultaneous load/archive branches
and their cancellation coordination. A later measured optimization can overlap them without
changing paths, payload bytes, or the completion contract.

## 2. Guarantee and non-goals

For an enabled GCS-staging write, every record covered by an emitted destination checkpoint must
have its existing BigQuery staging CSV representation durably archived in S3. Before ingestion,
the run must also have a durable schema descriptor and any requested generation cutoff.

This is an at-least-once archive of load inputs. It is not a transaction across BigQuery and S3,
nor evidence of final table publication. BigQuery may load data before S3 fails. Replays can
create duplicate rows/objects. Final merge, swap, or truncation can still fail after batch work.
Retain successful archive objects and cutoff events across errors, retries, refreshes, and CDC
deletes. Do not parse CDC rows into S3 deletions or delete a failed run's prefix.

Do not change customer BigQuery configuration, ingestion thresholds, formatter semantics, the
public specification, or the CDK version. Do not migrate BigQuery to the new dataflow engine as
part of this work. A shared toolkit extraction from Snowflake is also unnecessary for v1.

When copying is enabled with batched standard inserts, fail setup with a clear internal unsupported
strategy error. Silently skipping the archive would violate opt-in. `spec`, `check`, and disabled
writes must continue to work with either loading strategy and no AWS configuration.

## 3. Object layout and event consumption

Use the agreed Fusion contract:

```text
fusion/workspaces/<workspace_uuid>/sources/<source_uuid>/connections/<connection_uuid>/
  streams/<escaped_stream_name>/runs/<run_uuid>/
    schema.json
    generation-cutoff.json
    batches/<batch_uuid>.csv.gz
```

The prefix is configurable, defaulting to `fusion`. IDs are supplied by the platform, never
hardcoded or generated as a substitute for missing routing. A process generates one run UUID;
each completed GCS object gets one batch UUID reused throughout that archive transfer's retries.
Generation and sync IDs live in JSON/object metadata, not directory components. Exclude GCS
staging keys and temporary BigQuery table names from stable routing.

Preserve the original catalog stream name's case and UTF-8 bytes; percent-encode it as one key
component, including literal percent signs and slashes. Encode names equal to `.` or `..` fully.
An SDK may additionally URL-encode the resulting key for transport; consumers must distinguish
S3 notification encoding from the archive's component encoding. Do not lowercase or apply
BigQuery name munging. Record original/mapped namespace and name in JSON.

The name-only convention assumes unique stream names within a connection. Validate this at setup
and reject duplicate names across namespaces rather than allowing two streams to overwrite the
same run descriptor. This preserves the selected layout without relying on an unchecked catalog
assumption.

Write `schema.json` first and any cutoff second, once per stream/run, before setup returns.
Consumers of `batches/<uuid>.csv.gz` resolve `schema.json` in the parent run folder. Filter data
notifications to batch objects. Cutoff consumers handle `generation-cutoff.json` separately.
Do not rely on notification delivery order: the writes are ordered, but listeners must tolerate
duplicate and reordered events. Completed objects do not imply a successful overall sync.

Data objects use `application/gzip` without a `Content-Encoding` header. JSON uses
`application/json`. Data metadata includes `format-version`, `workspace-id`, `source-id`,
`connection-id`, `stream-key` (a short stable identity hash), `generation-id`, `sync-id`, `run-id`,
`batch-id`, and `schema-id`. Keep rich names and schemas out of S3 metadata headers.

Do not claim a formatter input count is available at the loader hook: `GcsBlob` contains the key
and storage configuration, not record counts. Record `loaded-record-count` from the completed
job's `outputRows`, explicitly documenting its meaning. Require zero bad records as today.
If an exact formatter-input count is later required, carry it through per-object accounting;
never count CSV lines, since quoted records can contain newlines.

## 4. Internal configuration and credentials

| Environment variable | Enabled-write requirement |
| --- | --- |
| `AIRBYTE_S3_COPY_ENABLED` | Defaults false; only explicit `true` or `false` accepted on writes |
| `AIRBYTE_S3_COPY_BUCKET` | Required archive bucket |
| `AIRBYTE_S3_COPY_REGION` | Required S3/STS region |
| `AIRBYTE_S3_COPY_ROLE_ARN` | Required target role |
| `AIRBYTE_S3_COPY_WORKSPACE_ID` | Required canonical UUID |
| `AIRBYTE_S3_COPY_SOURCE_ID` | Required canonical UUID of source actor |
| `AIRBYTE_S3_COPY_CONNECTION_ID` | Required canonical UUID |
| `AIRBYTE_S3_COPY_PREFIX` | Default `fusion`; trim surrounding slashes; reject empty |
| `AIRBYTE_S3_COPY_EXTERNAL_ID` | Optional STS external ID |

Check operation and enablement before binding enabled-only fields or constructing AWS clients.
Latch the configuration for the process. Validate all routing, supported generation combinations,
and supported strategy before records are consumed. A malformed enabled configuration fails the
write as an internal destination failure, not invalid customer Google credentials.

Use a dedicated Java AWS SDK v2 client with a pinned BOM starting at `2.46.0`, regional STS,
`DefaultCredentialsProvider.builder().build()`, and a refreshing assume-role provider. Set
asynchronous credential refresh, explicit Netty S3 and URL-connection STS transports, finite
standard retries (three total attempts), and explicit timeouts. Choose modern retry APIs; verify
with warnings treated as errors locally via an opt-in command, without changing repository-wide
warning policy.

**Keep GCS and AWS credentials/endpoints separate.**
[BigQueryBulkLoaderConfiguration.kt](src/main/kotlin/io/airbyte/integrations/destination/bigquery/write/bulk_loader/BigQueryBulkLoaderConfiguration.kt)
exposes S3 configuration backed by *GCS HMAC credentials and the Google storage endpoint*.
Do not reuse or replace those beans for the Fusion archive. Own the archive AWS clients inside
the connector-local service or qualify them explicitly. Current GCS internals use the Kotlin
AWS SDK and legacy dependencies; inspect resolved SDK, HTTP, Guava, Netty, and Jackson versions
before adding the Java SDK BOM. Do not add CRT dependencies for the archive path.

Platform companion work: inject the seven required routing/authorization values, gate enablement
on a connector version implementing this contract, and preserve them across job retries. In the
inspected platform checkout, `platform.inject-aws-secrets-to-connector-pods` enables standard
`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` injection for managed connectors in selected real
workspaces. Custom connectors are excluded. The launcher also needs its configured Kubernetes
secret. Verify the deployed data plane and identity; Google service-account credentials alone
are not AWS bootstrap credentials. Do not infer live flag state from checked-in configuration.

The role needs `s3:PutObject` and `s3:AbortMultipartUpload` only for the assigned archive prefix.
If the target bucket uses KMS, include the necessary key permissions. Provision trust and
incomplete-multipart cleanup separately. Consumer GetObject permissions belong to listener
identities, not this write-only role. Do not modify the Snowflake test role merely to implement
BigQuery; select the appropriate role/routing during deployment.

## 5. Integration points and lifecycle

Add a small connector-local `copy` package: gated configuration/factory, `BigqueryS3Copy`, immutable
stream/run context, metadata serializer/path builder, and a bounded closed-file uploader.
Use an injectable fake service for tests. Avoid a generic second batching system.

### Setup

[BigqueryBeansFactory.getWriter()](src/main/kotlin/io/airbyte/integrations/destination/bigquery/BigqueryBeansFactory.kt)
returns either CDK `DirectLoadTableWriter` or `TypingDedupingWriter`; there is no connector-local
BigQuery writer to patch. Wrap the chosen writer with one connector-local delegating writer:

1. Validate archive configuration, GCS strategy, stream-name uniqueness, and generation directives
   for the whole catalog. Disabled implementation does nothing.
2. Call the existing writer's `setup()`.
3. Derive contexts from the catalog and `TableCatalog`/column mapping without waiting for stream
   execution state. Upload all descriptors and cutoffs, with bounded or sequential metadata writes.
4. Publish immutable contexts and return from setup. Delegate `createStreamLoader()` unchanged.
5. Delegate teardown, closing the archive service in `finally`. The legacy writer signature is
   `teardown(destinationFailure: DestinationFailure?)`, not Snowflake's newer boolean signature.

The BigQuery checker calls a write operation internally; operation gating must still make archive
preparation a no-op for `check`. Test this wiring explicitly.

The current legacy CDK rejects empty catalogs before connector setup. For zero-row catalog streams,
upload schema and cutoff as usual. No event requires seeing a record.
Validate minimum generation zero or equal to current generation, preserving the direct/raw
loaders' unsupported-hybrid behavior. A cutoff event records `generation_cutoff_requested`, a
unique event ID, identities, run/sync/current/minimum generation IDs, and a strictly-less-than
discard instruction. It records a request even if final BigQuery refresh subsequently fails.

### Completed object load

Pass the stream's immutable context from `BigQueryBulkLoaderFactory.create()` to
`BigQueryBulkLoader`. Retain the existing execution-table selection.

Inside `load(remoteObject)`, keep job creation, job completion checks, and zero-bad-record checks.
Insert `archive.copyCompletedGcsObject(remoteObject, context, stats.outputRows)` before the existing
`GcsFilePostProcessing.DELETE` branch. Return only after that call and existing post-processing
complete. Do not log composite success before the archive finishes.

The archive call:

1. Acquire one of four process-wide transfer slots before creating a spool or reading GCS.
2. Allocate immutable batch ID/key and a unique temporary `.csv.gz` file.
3. Use the existing `GcsClient.get(key) { input -> ... }` to stream raw object bytes into the file
   with a bounded copy buffer on IO workers. Close input/output before starting S3. Do not
   materialize the object with `readBytes()`, parse it, decompress it, or recompress it.
4. Upload the closed file with a file-backed request body and immutable request metadata; await
   final object completion, including multipart completion.
5. Clean up the spool after all readers stop and release the slot. On failure, throw so the caller
   skips GCS deletion and cannot return a successful load result.

Unlike Snowflake, BigQuery does not already own a completed local gzip file at this hook. V1
deliberately adds **one compressed local spool per active archive copy**, one GCS GET, and one S3
upload. This costs disk and cross-cloud bandwidth but gives retries a seekable source and keeps
the change outside formatter/part-buffer ownership. Do not describe it as zero-spool copying.

GCS staging keys must remain immutable until copy and load finish. `GcsBlob` does not include a
GCS generation precondition. Validate the existing unique object-key behavior; if concurrent
replacement can occur, add generation-aware reads rather than silently archiving a different
object. Retain the source object on any archive failure. Respect the customer's existing KEEP
policy; DELETE executes only after both destinations succeed. Preserve existing deletion-error
behavior (failure after two successes may replay and duplicate data).

### Exact-byte and transfer bounds

GCS can serve decompressed bytes for gzip objects marked `Content-Encoding: gzip`. Verify the
actual staging headers and GET client behavior with a fixture and real service test. If needed,
request compressed bytes and disable client decoding; do not change stored objects globally or
recompress downloads to hide a mismatch. See [GCS transcoding documentation](https://docs.cloud.google.com/storage/docs/transcoding).

Use four copy slots, S3 HTTP concurrency 16, multipart threshold 64 MiB and minimum parts 16 MiB
as initial bounds. Explicitly enable multipart: a plain Java `S3AsyncClient.builder().build()`
does not enable it. See [AWS async multipart configuration](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/s3-async-client-multipart.html).
GCS factory targets currently are 200 MiB per object, 10/20 MiB parts for STDIO/socket, ten upload
workers, and one max concurrent table load in the ordinary pipeline. These are not hard limits
on compressed bytes; the socket one-shot path also needs the process-wide copy bound.

Add a hard spool-byte ceiling: start at 1 GiB per copy (four slots give at most 4 GiB, excluding
existing connector files), enforcing it while downloading. Exceeding it fails with a clear
internal resource error, retains the GCS source, and advances no checkpoint. Verify this budget
against the destination container's available ephemeral storage before rollout; the pilot can
adjust it. Do not let a small object-count semaphore stand in for a disk-byte bound.

Budget ten seconds for connection setup, two minutes per AWS request attempt, three total request
attempts, and thirty minutes for the archive operation including download, S3 multipart work,
and bounded cleanup. Preserve BigQuery's current ten-minute job timeout. Apply finite GCS read
timeouts/retries too. Retry a failed download from the start into a fresh/truncated task-owned
spool after the prior reader stops; never append a new download onto partial bytes. S3 retries
reuse the same complete file/key. Do not retry the whole BigQuery load after it has succeeded.

Coroutine/future cancellation is not evidence that file readers stopped. Track completion,
cancel/abort as supported, and drain with bounded cleanup. Retain a spool for container cleanup
when reader shutdown cannot be proved; then prevent new work from making retained resources
unbounded. Propagate cancellation. Provide idempotent close, normal teardown, a JVM shutdown
fallback, and explicit test cleanup for owned clients/providers/executors.

Implementation detail: SDK automatic multipart splitting of an arbitrary streaming body was not
retryable after a partially consumed part. `ArchiveFileBody` supplies seekable file ranges through
`splitCloseable`, reopening the same range on retries. Each subscription owns a bounded range and
closes on completion/cancellation; root cleanup drains readers and stream closers before unlinking.
Local HTTP tests exercise the real SDK/Netty multipart protocol, including partial-part retry and abort.

## 6. Schema descriptor

Use a versioned `bigquery-gcs-load-csv-gzip-v1` format, distinct from Snowflake's CSV contract.
Include connector version, loading strategy, direct/raw mode, input format, all routing IDs,
original/mapped stream identity, logical project/dataset/table, generation and sync IDs, run ID,
and a stable layout `schema_id`. Compute the ID over a canonical layout body excluding run,
sync, generation, and other attempt-specific fields; keep column-array order.

Derive the ordered CSV header from the same `stream.schema.withAirbyteMeta(...)` and header helper
used by `BigQueryObjectStorageFormattingWriter` / its protobuf variant. Derive load types from
`BigQueryRecordFormatter.getDirectLoadSchema(stream, mapping)` in schema mode, and `CSV_SCHEMA`
in raw mode. Record **CSV ordinal/header and target field name separately**: source header names
can differ from mapped BigQuery field names, and the load job skips the header. Record types,
field modes/nullability, nested field schemas where applicable, and input-to-target mapping.

Raw mode's CSV order is `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_meta`,
`_airbyte_generation_id`, `_airbyte_data`. It omits `_airbyte_loaded_at`, even though that field
exists in `SCHEMA_V2`. Do not use the final raw-table schema as the CSV descriptor.

Include `import_type`, configured `primary_key` paths, and configured `cursor` path. Preserve
original paths and their target-column mapping for direct mode. In raw mode identify those as
paths inside `_airbyte_data`, not nonexistent top-level CSV columns. Empty arrays indicate no
configured key/cursor. Record CDC mode where it affects consumers; distinguish configured cursor
from any extracted-at fallback used during deduplication. This explicitly supplies information
missing from the current Snowflake preview descriptor.

The legacy CDK drops configured keys/cursors from its `DestinationStream` for append streams.
Read these fields from the original `ConfiguredAirbyteCatalog` and match by original stream identity.
Descriptor serialization preserves explicit nulls with the same Jackson mapper used for hashing;
the CDK's default null-omitting serialization would change the published layout's hash.

Describe UTF-8, gzip, one header row, separator, quote/escape behavior, line separator, and null
representation from actual formatter fixtures. The writer uses the shared Apache Commons CSV
helper with NON_NUMERIC quoting, not Snowflake's FastCSV writer. Direct row generation uses
`\N` as the null marker; verify raw and protobuf bytes independently. Do not normalize output
merely to fit the descriptor. State known lost distinctions and serialized JSON/time conversions.

Record the explicit load settings in agreement with `BigQueryBulkLoader`: CSV,
`skipLeadingRows=1`, `allowQuotedNewLines=true`, `allowJaggedRows=true`,
`preserveAsciiControlCharacters=true`, `nullMarker=\N`, and `WRITE_APPEND`.
Label unspecified server options as inherited defaults. Add a small connector-local layout helper
or contract test to prevent schema/formatter/job options drifting independently. Do not promise
the descriptor reproduces every server conversion or the final table snapshot.

## 7. Checkpoint proof and failure behavior

BigQuery is using the **legacy task pipeline**, not Snowflake's new `StateStage` path.
The relevant CDK sources under `airbyte-cdk/bulk/toolkits` are:

- `legacy-task-load-db/.../pipeline/db/BulkLoaderTableLoader.kt`: `accept()` awaits `load()` before
  returning `IntermediateOutput(..., LoadResult)`; `LoadResult` is `BatchState.COMPLETE`.
- `legacy-task-load-db/.../write/db/BulkLoader.kt`: GCS upload completion alone is `BatchState.LOADED`.
- `legacy-task-loader/.../task/internal/LoadPipelineStepTask.kt`: carries checkpoint counts through
  accumulator accept/finish and publishes returned batch state through `handleOutput()`.
- BigQuery's socket `BigQueryBulkOneShotUploader` waits for part completion, then calls the same
  bulk loader before emitting `FinalOutput(LoadResult)`, including its EOF `finish()` path.

Thus the common `load()` hook is the intended completion gate, but confirm with a real pipeline
test: a mock loader unit test alone is insufficient. Check EOF and the ordinary table loader's
empty finish output cannot publish counts from a failed/incomplete archive.

Zero-record checkpoints are already eligible in the legacy checkpoint manager before setup finishes.
`BigqueryCopyCheckpointConsumer` therefore gates actual checkpoint emission on metadata readiness.
On failed/cancelled setup it frees reservations without acknowledging state, including the failure
task's final checkpoint flush. Normal records still use the existing per-batch completion accounting.
Failed-sync teardown logs secondary cleanup errors and returns so the legacy launcher can receive
its failure-completion signal. A client constructed concurrently with close is closed before use.

| Failure point | Outcome |
| --- | --- |
| Descriptor/cutoff write | Setup fails, including zero-row refreshes; keep metadata already written |
| GCS upload or BigQuery load | Existing failure; no successful archive load result required |
| GCS GET / spool / S3 upload after BigQuery success | Fail batch, retain GCS source, keep any completed S3 object, no complete checkpoint counts |
| GCS DELETE after both successes | Preserve existing failure semantics; archive remains |
| Process death after archive success, before state | Normal replay can duplicate records and objects |
| Final table refresh/merge failure | Existing retry semantics; keep archives and requested cutoff |

Do not issue archive deletes. Earlier independent checkpoints whose work completed may still be
emitted. Do not log an S3 failure as a customer BigQuery credential error.

## 8. Test plan and acceptance criteria

Deterministic connector tests must cover:

1. Exact gzip-byte identity: build the real formatter/compressor output, fake GCS GET, capture S3
   request bytes, compare bytes and parse the decompressed CSV. Include headers, Unicode, delimiters,
   embedded newlines, null/empty/literal null-marker strings, timestamps, nested values, Airbyte
   metadata, and generation. Cover JSON/protobuf and schema/raw output combinations.
2. Common load gate: block S3 after a successful BigQuery job; load must remain incomplete and GCS
   deletion absent. Release and assert upload → optional DELETE → return. Fail each operation,
   including multipart completion and cleanup, and verify no connector-issued duplicate load job.
3. Request identity: SDK retries keep key/metadata/file; distinct objects/runs have distinct UUIDs.
   A failed download leaves no partial file eligible for upload. Assert the spool byte cap.
4. Setup: schema before batches, cutoff strictly below minimum, minimum zero emits none, metadata
   failure blocks ingestion, duplicate stream-name routing rejected, unsupported hybrids preserve
   existing behavior, and zero-row refreshes still get metadata.
5. Descriptors: real header ordinals versus mapped fields, raw CSV versus final raw schema,
   source/target primary key and cursor mapping, null namespace, escaped names, schema hash
   stability across runs, and layout changes changing the hash.
6. Disabled/spec/check: no AWS construction, no extra GCS GET/spool, unchanged public specs.
   Include checker-internal write operations. Enabled standard inserts fail before ingestion.
7. Lifetime and pressure: four copies max across socket partitions, metadata concurrency bounded,
   cancellation before/while reading, a cancelled future with an active reader, drained readers
   before unlink, client shutdown idempotence, no unbounded orphan copies.
8. Actual legacy pipeline checkpoint tests: feed records and states under STDIO and socket paths,
   hold the archive response, and assert no covering state until load completes. Include EOF
   partial batches, multiple streams/partitions, global states, archive failure, BigQuery failure,
   and zero-row cutoff failure. Assert object-upload `LOADED` is not final `COMPLETE`.

Real-service pre-rollout validation: GCS HMAC read access, exact compressed download without
transcoding, BigQuery append/dedup/refresh/schema-evolution/raw results, both GCS KEEP/DELETE,
AWS role trust and expired credentials, forced multipart and abort, and a run spanning credential
refresh. Use separate consumer credentials to inspect S3. Load-test disabled/enabled throughput,
cross-cloud bytes, peak spool size, heap, throttling/backpressure, and checkpoint latency.

Commands from the repository root:

```sh
./gradlew :airbyte-integrations:connectors:destination-bigquery:test
./gradlew :airbyte-integrations:connectors:destination-bigquery:integrationTestNonDocker
./gradlew :airbyte-integrations:connectors:destination-bigquery:dependencies --configuration runtimeClasspath
```

Service integration checks need configured test accounts/resources. Compare both spec snapshots
unchanged. Verify strict compilation using local CI-equivalent configuration before publishing.

Validation performed during implementation: deterministic unit/pipeline tests, SDK multipart tests
against a local HTTP fixture, and live GCS-to-BigQuery-to-S3 writes for direct JSON/STDIO, direct
protobuf/socket, and raw JSON/STDIO. S3 inspection verified gzip/header/row-count metadata and
recomputed each schema hash. A live empty truncate refresh produced a durable schema/cutoff with no
batch object and completed successfully. OSS and Cloud spec snapshots were unchanged. Test settings were
provided only through the local environment using a validation prefix. Long-duration credential
refresh, production-scale throughput/disk budgets, and the full service failure matrix remain
pre-rollout checks; a small successful smoke test does not establish them.

## 9. Delivery sequence and rollout

1. Add gated archive configuration, isolated AWS dependencies/client owner, paths, serializers,
   and tests. Inspect dependency resolution; retain the CDK/toolkit selections.
2. Add the delegating writer and durable run schema/cutoff preparation. Share layout derivation
   between descriptors and existing loader factories without rewriting record formatting.
3. Add the common completed-GCS-object archive hook, spool/transfer limits, deferred GCS cleanup,
   and deterministic load/checkpoint tests. Keep standard inserts explicitly unsupported when enabled.
4. Provision role/trust and prefix/lifecycle, inject IDs and bootstrap credentials for a pilot
   workspace, verify live role assumption, then test real GCS/BigQuery/S3 failure cases.
5. Add startup enablement/version logging; log run/batch/key and archive start/success/failure,
   bytes and duration, and metadata completion. Add counters/timers for downloads, archives,
   retries, slot wait, failures, and retained spool bytes. IDs belong in logs, not metric labels.
6. Publish a preview and inspect both pipeline checkpoints and S3 output before enabling more
   connections. Never automatically disable copying on failures. A rollback disables future
   copies and leaves existing archive objects intact.

Acceptance requires durable per-run metadata, exact completed-GCS-object bytes for every covered
checkpoint, no premature GCS deletion or spool unlink, bounded resources under throttling and
cancellation, and verified credential refresh. Passing a unit suite or publishing an image alone
does not establish this contract. Current Snowflake uploader cancellation/multipart gaps must not
be copied as a production-ready implementation.

## 10. Subsequent standard-insert work

After GCS staging passes the pilot, define `bigquery-load-ndjson-v1` and archive `.jsonl` (or a
separately specified compressed representation) from exactly the UTF-8 bytes already produced in
`BigqueryBatchStandardInsertsLoader.accept()`. Preserve the current line separator. Tee into an
owned bounded spool while retaining the existing buffer/channel threshold; avoid a second record
serialization. Gate `finish()` on both job completion and archive completion and test every buffer
transition, empty batch, EOF, both record formatters, both table modes, and failure cleanup.
Reuse run routing, control metadata, configuration, and consumer dispatch by format ID. Do not
label NDJSON as CSV or infer its layout from a GCS CSV descriptor.
