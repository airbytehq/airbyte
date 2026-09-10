import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Ashby Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 declares item schemas for 14 previously-untyped array columns across seven streams. This is a breaking change for affected data-lake destinations.

### What changed

The following array columns now declare object elements with their individual fields:

- `applications.customFields`
- `applications.hiringTeam`
- `candidates.customFields`
- `candidates.emailAddresses`
- `candidates.fileHandles`
- `candidates.phoneNumbers`
- `candidates.socialLinks`
- `candidates.tags`
- `interview_schedules.interviewEvents`
- `jobs.customFields`
- `jobs.hiringTeam`

These columns declare object elements without declaring the fields inside them:

- `custom_fields.selectableValues`
- `offers.versions`
- `users.customFields`

### Why this changed

The connector now declares documented Ashby API fields and the schemas of their array elements. These declarations re-type the affected columns from untyped arrays to typed arrays on S3 Data Lake and Iceberg destinations.

### Who is affected

This change affects connections that write the `applications`, `candidates`, `custom_fields`, `interview_schedules`, `jobs`, `offers`, or `users` streams to S3 Data Lake or Iceberg destinations. Other destinations, including BigQuery and Snowflake, are unaffected because they map typed and untyped arrays identically.

The registry breaking-change notice for 1.0.0 lists only `applications`, `candidates`, and `jobs`. Treat the list above as authoritative: it reflects every array column that gained an element schema in the 1.0.0 manifest.

### Required actions

1. Refresh the source schema for the affected streams.
2. If a sync fails with a schema-evolution error, drop and recreate the affected destination tables.

## Connector upgrade guide

<MigrationGuide />
