import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# GitHub Migration Guide

## Upgrading to 2.0.0

This release renames reaction fields in GitHub API responses to comply with Avro naming standards, which are required for destinations like S3 Parquet and Avro.

### Breaking Changes

The reaction fields `+1` and `-1` have been renamed to `thumbs_up` and `thumbs_down` respectively. These field names appear in the `reactions` object across multiple streams including:

- Comments
- Commit comments
- Issues
- Pull requests
- Reviews
- All event streams containing comment data

Avro field names must match the pattern `[A-Za-z_][A-Za-z0-9_]*`, which does not allow field names starting with special characters like `+` or `-`. The new names `thumbs_up` and `thumbs_down` directly correspond to GitHub's reaction emoji names and maintain semantic clarity.

### Migration Steps

After upgrading to version 2.0.0:

1. **Refresh your source schema** in the Airbyte UI to recognize the renamed fields
2. **Reset affected streams** to ensure consistent data with the new field names
3. **Update any downstream transformations or queries** that reference the old field names `+1` or `-1` to use `thumbs_up` and `thumbs_down`

## Connector upgrade guide

<MigrationGuide />
