# Google Cloud Storage (GCS) Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 re-implements destination-gcs on Airbyte's **Bulk Load CDK** (the same engine as
destination-s3 v1.x), replacing the legacy Java CDK. The goal is significantly higher throughput on
large syncs, achieved by a parallel, back-pressured multipart-upload pipeline instead of the old
single-stream uploader.

### What is preserved (no action needed)

- **Authentication** is unchanged: HMAC keys over the GCS S3-interoperability endpoint
  (`credential.credential_type = HMAC_KEY`, `hmac_key_access_id`, `hmac_key_secret`). Existing
  configs keep working.
- **Formats and codecs**: Avro, CSV, JSONL, Parquet, with the same compression options — including
  **Avro + snappy** (the snappy codec still lives inside the Avro container; the object extension
  stays `.avro`).
- **Output layout**: data is still written under `<gcs_bucket_path>/<namespace>/<stream>/` with
  name-transformed path segments.

### Output paths and file names

With the same config as 0.4.x (path template in `gcs_bucket_path`, `gcs_path_format` left empty),
the directory layout and first object name remain unchanged for Avro, Parquet, and uncompressed
CSV or JSONL output. The connector still uses the
`${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_` path format and a `0` part-number
suffix for the first object.

CSV and JSONL now use GZIP compression by default, so their default extensions change from `.csv`
and `.jsonl` to `.csv.gz` and `.jsonl.gz`. Larger streams can also create additional objects with
part-number suffixes such as `1` and `2`.

### What changes

- A stream larger than ~200 MB is now split into multiple objects (`..._0`, `..._1`, …) using the
  S3-style part-number suffix, instead of one large file — so consumers should read **all** objects
  under a stream's prefix.
- **Record metadata fields changed** in every output format: `_airbyte_ab_id` is renamed to
  `_airbyte_raw_id`, `_airbyte_emitted_at` is renamed to `_airbyte_extracted_at`, and
  `_airbyte_generation_id` and `_airbyte_meta` are added. Update downstream consumers that read
  these fields by name.
- CSV and JSONL are **GZIP-compressed by default** (`.csv.gz` / `.jsonl.gz`); set
  `format.compression.compression_type = "No Compression"` for uncompressed output. Avro and Parquet
  are not affected (their compression is internal to the container).

:::warning
After an append sync upgrade, a stream prefix can contain both legacy 0.4.x objects and new 1.0.0
objects. These objects can use different compression and Airbyte metadata fields. Ensure downstream
consumers can read both formats, use a new bucket path for 1.0.0 output, or run a Full Refresh -
Overwrite sync to clear the existing stream prefix before writing 1.0.0 objects.
:::

### Configuration changes

- **Removed**: The `part_size` field has been removed. The connector now uses tuned internal defaults
  and exposes no performance-tuning settings. Existing configs that include `part_size` will have the
  field ignored.
- **New**: `gcs_path_format` — optional field to customize the directory layout under the bucket
  path. Defaults to `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_`, matching
  v0.4.x behavior. See the
  [GCS Path Format](gcs.md#gcs-path-format) documentation for available variables.
- **New**: `file_name_pattern` — optional field to customize output file names. Defaults to
  `{part_number}{format_extension}`. See the
  [File Name Pattern](gcs.md#file-name-pattern) documentation for available variables.
- **Changed**: `gcs_bucket_region` is now optional with a default of `"us"`. Existing configs that
  include this field are unaffected.
- **Changed**: CSV's `flattening` property is now required, but it defaults to `"No flattening"`.
  Existing CSV configs therefore remain valid without changes.

### Upgrading

Review your downstream consumers to make sure they:

- Read every object under a stream's prefix instead of assuming one file per stream.
- Use the new Airbyte metadata field names.
- Support GZIP-compressed CSV and JSONL output, or configure `"No Compression"`.
- Account for mixed 0.4.x and 1.0.0 objects after append syncs, or start 1.0.0 writes in a clean
  stream prefix.

No connector configuration change is required, but downstream readers may require changes.
