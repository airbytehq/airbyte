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
object keys are byte-for-byte identical to 0.4.x, including the `<date>_<epoch>_0.<ext>` file name
and the directory layout — verified against a real 0.4.x production object. `gcs_bucket_path` is now
a substituted path template composed with `gcs_path_format`; when `gcs_path_format` is empty it
falls back to `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_`, exactly reproducing
0.4.x behaviour (namespace/stream appended after the bucket-path template).

### What changes

- A stream larger than ~200 MB is now split into multiple objects (`..._0`, `..._1`, …) using the
  S3-style part-number suffix, instead of one large file — so consumers should read **all** objects
  under a stream's prefix.
- CSV and JSONL are **GZIP-compressed by default** (`.csv.gz` / `.jsonl.gz`); set
  `format.compression.compression_type = "No Compression"` for uncompressed output. Avro and Parquet
  are not affected (their compression is internal to the container).

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

### Upgrading

Review your downstream consumers to make sure they read every object under a stream's prefix (rather
than assuming a single file per stream), and confirm the default CSV/JSONL GZIP compression matches
your expectations. No configuration change is required for the upgrade itself — existing configs are
fully compatible.
