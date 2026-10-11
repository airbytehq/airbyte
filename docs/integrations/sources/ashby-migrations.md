import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Ashby Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 declares item schemas for ten previously-untyped array columns across the `applications`, `candidates`, and `jobs` streams. This is a breaking change for affected data-lake destinations.

### What changed

The following array columns now declare their element schemas:

- `applications.customFields`
- `applications.hiringTeam`
- `candidates.customFields`
- `candidates.emailAddresses`
- `candidates.fileHandles`
- `candidates.phoneNumbers`
- `candidates.socialLinks`
- `candidates.tags`
- `jobs.customFields`
- `jobs.hiringTeam`

### Why this changed

The connector now declares documented Ashby API fields and the schemas of their array elements. These declarations re-type the affected columns from untyped arrays to typed arrays on S3 Data Lake and Iceberg destinations.

### Who is affected

This change affects connections that write the `applications`, `candidates`, or `jobs` streams to S3 Data Lake or Iceberg destinations. Other destinations, including BigQuery and Snowflake, are unaffected because they map typed and untyped arrays identically.

### Required actions

1. Refresh the source schema for the affected streams.
2. If a sync fails with a schema-evolution error, drop and recreate the affected destination tables.

## Connector upgrade guide

<MigrationGuide />
