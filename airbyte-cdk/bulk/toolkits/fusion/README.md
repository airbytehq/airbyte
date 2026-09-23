# Fusion archive toolkit

Shared environment configuration, S3 run paths, metadata and uploads for destination archives.
This module has no dependency on either legacy or bulk CDK core/protocol models. Connectors
retain their serialization, schema descriptor, hashing, batching and success lifecycle logic.

## Consumption and prerelease builds

For the dependent connector PRs, merge the common CDK commit into each branch, then add an
explicit dependency (Kotlin DSL shown; Groovy uses the same project path):

```kotlin
implementation(project(":airbyte-cdk:bulk:toolkits:bulk-cdk-toolkit-fusion"))
```

Keep existing `cdkVersion` / `cdkVersionRequired` unchanged. Do not add `fusion` to the bulk
connector `toolkits` list: that mechanism uses the connector's core CDK version.

The connector prerelease workflow checks out `refs/pull/{pr}/head`, then the Java publishing
script runs the connector's Gradle `assemble` task from the full repository checkout. The
explicit project dependency builds this toolkit and includes its JAR and runtime dependencies
in the connector distribution/image. The shared commit must therefore be present in each
connector PR's branch; a sibling worktree or local Maven publication is insufficient.

This toolkit is independently versioned as
`io.airbyte.bulk-cdk:bulk-cdk-toolkit-fusion:0.1.0-fusion.1`. It inherits the bulk CDK CloudRepo
publication configuration. To publish only this module with the standard CloudRepo credentials:

```sh
./gradlew :airbyte-cdk:bulk:toolkits:bulk-cdk-toolkit-fusion:publish
```

Only after that artifact has been published can a connector replace the project dependency
with those Maven coordinates. Existing base/extract/load aggregate publishing workflows do
not publish this independently versioned module. No publication is required for the project
consumption described above.

## Configuration and APIs

`FusionConfiguration.fromEnvironment(env)` returns null when `AIRBYTE_S3_COPY_ENABLED` is
absent or `false`. When enabled (`true`), it requires `AIRBYTE_S3_COPY_ROLE_ARN`,
`AIRBYTE_S3_COPY_BUCKET`, `AIRBYTE_S3_COPY_REGION`, and canonical UUIDs in
`AIRBYTE_{ORGANIZATION,WORKSPACE,SOURCE,CONNECTION,DESTINATION}_ID`.
There are no specification overrides or invented identity values.
`AIRBYTE_S3_COPY_PREFIX` defaults to `fusion`.

`AWS_ASSUME_ROLE_EXTERNAL_ID` supplies the STS external ID. If the paired
`AWS_ASSUME_ROLE_ACCESS_KEY_ID` and `AWS_ASSUME_ROLE_SECRET_ACCESS_KEY` are provided, they
bootstrap STS. If both are absent, the AWS default credentials provider chain is used.
A partially supplied pair fails configuration validation. Secrets are not included in a
generated configuration `toString`.

`FusionPaths.run(config, streamName, runId, epochSeconds)` returns:

```text
{prefix}/organizations/{id}/workspaces/{id}/sources/{id}/connections/{id}/destinations/{id}/syncs/streams/{escaped}/runs/{epoch}/{uuid}/
```

Stream names are percent escaped UTF-8 key components. Paths reserve space for a batch UUID
and `.jsonl.gz` suffix within the S3 1024-byte key limit.

`FusionSchema.fromConfiguredStream(configuredStream: JsonNode)` extracts the original
`stream.json_schema`, `primary_key` and `cursor_field` into `source_schema`, `primary_key`
and `cursor`. Missing keys/cursors become empty lists; schema annotations are preserved.
Use your JSON mapper to turn the configured protocol stream into a tree, then combine this
map with the connector descriptor.

`FusionMetadata(config, runId, epochSeconds)` exposes:

- `schema(descriptor, schemaId, generationId, syncId)`: adds authoritative identity,
  run, schema and generation fields. Descriptor must contain `source_schema`, `primary_key`,
  and `cursor`; connector-specific fields are retained.
- `streamComplete(jobId, minGenerationId = null)`: returns `job_id` and only adds
  `min_generation_id` for a positive minimum generation.
- `batch(streamKey, generationId, syncId, schemaId, recordCount: Long, batchId)`:
  shared S3 metadata headers.

`FusionUploader` exposes asynchronous file and JSON byte uploads. `S3FusionUploader(config,
contentType = "application/gzip")` assumes the configured role and owns/closes its clients.
Serialize metadata with the connector's existing JSON mapper. Await uploads before emitting
successful state and write `{runPath}batches/stream_complete.json` only after successful
stream completion, including empty streams.
