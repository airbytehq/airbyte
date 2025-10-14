import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# GitHub Migration Guide

## Upgrading to 2.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we have updated the GitHub source connector to normalize reaction field names for compatibility with Avro and Parquet destinations (such as S3, BigQuery, Snowflake, etc.).

This release introduces breaking changes to the `reactions` object schema, which appears in multiple streams. The GitHub API returns reaction fields named `+1` and `-1`, but these field names violate the Avro specification and cause duplicate field errors when syncing to Parquet/Avro destinations. Both `+1` and `-1` get normalized to `_1`, resulting in a "Duplicate field _1" error that breaks syncs.

### What changed

The reaction fields have been renamed for Avro compatibility:
- `+1` → `plus_one`
- `-1` → `minus_one`

### Affected streams

All streams containing the `reactions` object are affected:
- `comments`
- `commit_comments`
- `issue_events`
- `issues`
- `releases`
- `review_comments`

### Required actions

After upgrading to version 2.0.0:

1. **Refresh your source schema** in the Airbyte UI to see the updated field names
2. **Reset affected streams** to re-sync data with the new field names (recommended if you need historical data with the corrected schema)
3. **Update downstream queries and dashboards** that reference the old `+1` and `-1` fields to use `plus_one` and `minus_one` instead

### Migration timeline

You have until **2025-11-14** to upgrade to version 2.0.0. After this date, the connector may be automatically upgraded to the latest version.

## Connector upgrade guide

<MigrationGuide />
