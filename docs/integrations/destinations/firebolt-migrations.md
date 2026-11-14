import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Firebolt Migration Guide

## Upgrading to 0.3.0

Version 0.3.0 is a full rewrite of the Firebolt destination: the original Python connector is replaced by a Java/Kotlin connector built on Airbyte's bulk-connector CDK (DirectLoad).

### What changed

- **Table format**: each stream now writes a final table with typed columns matching the stream schema, instead of a single raw table containing one JSON blob per record. Final tables carry the Airbyte metadata columns `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_meta`, and `_airbyte_generation_id`.
- **Load mechanism**: data is buffered into gzipped CSV files, uploaded to an S3 staging bucket, and loaded with Firebolt `COPY FROM`, replacing the previous row-by-row SQL `INSERT` path.
- **Configuration**: S3 staging configuration (`s3_staging`) is now required for every connection. New optional fields `schema` (default namespace) and `jdbc_url_params` are available; the S3 credentials are grouped under the `s3_staging` object.
- **Sync modes**: `Incremental | Append + Deduped` is now supported and merges staged rows into the final table.

### Why

The rewrite moves the connector onto the actively maintained bulk-connector framework, gives streams a typed final-table layout compatible with standard downstream tooling, and replaces per-row inserts with set-based `COPY FROM` loads for substantially better throughput.

### Who is affected

Every connection using the Firebolt destination:

- Connections must add S3 staging configuration or syncs will fail after upgrade.
- Streams upgraded in place produce tables in the new typed format alongside the old raw tables; existing raw tables are not migrated or modified.

### Migration steps

1. Before upgrading, note each connection's existing configuration.
2. Upgrade the connector to 0.3.0.
3. Edit each Firebolt destination/connection and fill in the required `s3_staging` fields (bucket name, region, access key id, secret access key; optionally bucket path, filename pattern, and purge behavior). Set `schema` if streams should land in a specific Firebolt schema.
4. Run a full refresh of each connection so stream data is rewritten into the new final tables.
5. After verifying the new tables, drop the old raw Firebolt tables created by previous versions.

## Connector upgrade guide

<MigrationGuide />
