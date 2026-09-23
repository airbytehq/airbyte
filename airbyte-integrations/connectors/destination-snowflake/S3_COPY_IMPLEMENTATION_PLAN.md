# Snowflake Fusion copy

For an enabled write, Snowflake uploads the existing closed gzip CSV to S3 and loads it into Snowflake. A batch completes only after both operations succeed. The existing CDK checkpoint boundary therefore covers the durable copy. This is at-least-once delivery, not a transaction across Snowflake and S3: retries can leave duplicate objects or objects from failed runs.

## Shared CDK contract

The `airbyte-cdk/bulk/toolkits/fusion` toolkit owns environment parsing, AWS credentials and uploading, key escaping and layout, run identity, schema metadata, and stream completion payloads. Snowflake depends on this standalone toolkit without changing its core load CDK version. The dependent PR includes the shared commit so preview builds work directly from the checkout.

All routing comes from the environment. There are no Fusion destination configuration properties or hardcoded enabled settings, buckets, role ARNs, credentials, or identity values.

| Variable | Behavior |
| --- | --- |
| `AIRBYTE_S3_COPY_ENABLED` | Absent or `false` disables copying; `true` enables it. Other values fail validation. |
| `AIRBYTE_S3_COPY_BUCKET` | Required when enabled. |
| `AIRBYTE_S3_COPY_REGION` | Required when enabled. |
| `AIRBYTE_S3_COPY_ROLE_ARN` | Required when enabled. |
| `AIRBYTE_S3_COPY_PREFIX` | Defaults to `fusion`; surrounding slashes are normalized. |
| `AIRBYTE_ORGANIZATION_ID` | Required canonical UUID when enabled. |
| `AIRBYTE_WORKSPACE_ID` | Required canonical UUID when enabled. |
| `AIRBYTE_SOURCE_ID` | Required canonical UUID when enabled. |
| `AIRBYTE_CONNECTION_ID` | Required canonical UUID when enabled. |
| `AIRBYTE_DESTINATION_ID` | Required canonical UUID when enabled. |
| `AWS_ASSUME_ROLE_ACCESS_KEY_ID`, `AWS_ASSUME_ROLE_SECRET_ACCESS_KEY` | Optional paired platform bootstrap credentials; otherwise use the ambient AWS credential provider chain. |
| `AWS_ASSUME_ROLE_EXTERNAL_ID` | Optional external ID passed to STS AssumeRole. |

The write-only factory initializes Fusion before ingestion. Spec and check commands do not need archive credentials. The bootstrap identity needs permission to assume the copy role; the role's trust policy must allow that identity and any external-ID condition. The assumed role needs access to the configured bucket. Standard AWS SDK endpoint configuration supports local test services without connector-specific overrides.

## Object layout

```text
s3://{bucket}/{prefix}/organizations/{organization_id}/workspaces/{workspace_id}/sources/{source_id}/connections/{connection_id}/destinations/{destination_id}/syncs/streams/{escaped_stream}/runs/{epoch}/{run_uuid}/
  schema.json
  batches/
    {batch_uuid}.csv.gz
    stream_complete.json
```

Snowflake always writes under `syncs`. The epoch is captured once with `Instant.now().epochSecond` alongside a generated run UUID when the write service is created. All streams share that run identity. Original stream names preserve case and use percent-encoded UTF-8 components. Before writing sidecars, setup validates every stream's path against S3's 1,024-byte key limit, reserving room for batch suffixes.

## Schema and completion

Setup writes `schema.json` before batches. It includes:

- `contract_version`, `connector`, `format`, and CSV `dialect`.
- Original `stream`, `mapped_stream`, final `table`, raw/schema `mode`, ordered `columns`, and `input_to_final` mappings.
- `source_schema`, preserving the configured catalog's original JSON Schema in raw and typed modes. A CDK input-schema conversion is the fallback when a configured catalog is unavailable.
- `primary_key` and `cursor` from the configured stream, including append streams.
- Five routing IDs, `run_id`, `epoch_seconds`, `schema_id`, `generation_id`, and `sync_id`.

The schema ID hashes the stream descriptor. Batches contain the identical compressed bytes used for Snowflake loading; copying adds no record serialization or recompression. S3 batch metadata includes run identity, stream/schema/batch IDs, generation and sync IDs, record count, and format version.

After successful stream finalization, the connector writes `batches/stream_complete.json` containing `job_id` (the catalog sync ID) and optional positive `min_generation_id`. Empty successful streams also receive a marker. Failed marker uploads remain retryable; successful markers are written once. A worker finds a batch's schema in the parent of its `batches` directory.

## Connector integration and validation

`SnowflakeWriter.setup()` prepares schemas before ingestion. `SnowflakeAggregateFactory` passes immutable stream context to `SnowflakeInsertBuffer`. The buffer closes the CSV, performs both durable operations, and retains the file until both readers finish. Existing flush/checkpoint behavior applies to STDIO and socket inputs. Both legacy raw tables and schema mode retain the original source schema.

Shared toolkit tests cover configuration, escaping, identity and schema requirements. Focused Snowflake tests cover descriptor contents, original schemas and keys/cursors, empty streams, completion retries, and batch integration. GitHub runs the broader suites and preview publishing; local checks do not require production warehouse credentials.
