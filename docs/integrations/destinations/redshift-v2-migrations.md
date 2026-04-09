# Redshift Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 is a full rewrite of the Redshift destination using the new CDK architecture. Key changes:

- **No raw tables** — data is written directly to final tables instead of staging through `_airbyte_raw_*` tables
- **Same configuration** — the spec is unchanged, so no configuration updates are needed
- **Improved error handling** — the connection checker now validates the full S3 staging → COPY → Redshift pipeline with clear error messages

### Migration steps

TBD
