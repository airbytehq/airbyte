# Redshift V2 Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 is a full rewrite of the Redshift destination using the new CDK architecture. Key changes:

- **No raw tables** — data is written directly to final tables instead of staging through `_airbyte_raw_*` tables
- **Same configuration** — the spec is unchanged, so no configuration updates are needed
- **Improved error handling** — the connection checker now validates the full S3 staging → COPY → Redshift pipeline with clear error messages

### Migration steps

1. Upgrade the destination to version 4.0.0
2. Trigger a full refresh sync for all connections using this destination
3. Verify data in the final tables
4. Update any downstream dbt models or SQL queries that reference `_airbyte_raw_*` tables
5. Optional: Drop old raw tables (`_airbyte_raw_*`) after verifying the new tables
