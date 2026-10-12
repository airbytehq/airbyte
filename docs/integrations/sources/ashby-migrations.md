import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Ashby Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 corrects four stream schemas. These type and field changes affect every destination; they are not limited to data-lake destinations.

### What changed

- `applications.archiveReason` changes from a string to an object with `id`, `text`, `reasonType`, `isArchived`, and `customFields` fields.
- `job_postings.publishedDate` changes from a date-time to a date.
- `application_criteria_evaluations` gains a primary key of `application_id` and `id`. Connections that use a deduplicated sync mode can now key this stream on those fields; earlier versions had no primary key.
- `application_criteria_evaluations` removes the never-populated `assessmentType`, `criterionName`, and `jobId` columns.
- `interviews` removes the never-populated `applicationId`, `interviewScheduleId`, `interviewStageId`, `status`, `createdAt`, `updatedAt`, `cancelledAt`, `startTime`, `endTime`, `feedbackLink`, `interviewerUserIds`, and `meetingLink` columns.

The removed interview scheduling fields that are available elsewhere are on `interview_schedules`: `applicationId`, `interviewStageId`, `status`, `createdAt`, and `updatedAt` are top-level fields. `startTime`, `endTime`, `feedbackLink`, `interviewerUserIds`, `meetingLink`, and `interviewScheduleId` are fields on objects in its `interviewEvents` array. `cancelledAt` has no direct replacement; cancellation is reflected in the schedule's `status`.

### Why this changed

The schemas now match the fields and types returned by Ashby's API. The criteria-evaluation primary key also gives connections that use a deduplicated sync mode a source-defined key for evaluation records.

### Who is affected

Anyone syncing `applications`, `job_postings`, `application_criteria_evaluations`, or `interviews` is affected. The type changes and removed columns apply to all destination types, not only data lakes. Connections that don't sync these four streams are unaffected.

### Required actions

1. Refresh the source schema for all four affected streams.

   Existing `applications` rows keep their previous `archiveReason` value until the application next changes in Ashby, because `applications` syncs incrementally. To rewrite every row in the new shape, refresh the `applications` stream. The re-sync re-reads applications created after your start date. Applications deleted in Ashby since your last sync don't return.

2. `application_criteria_evaluations` is a full-refresh stream, so the new primary key applies on the next sync and no reset is needed. If you sync it with Full refresh | Append, don't clear it. The connector only returns evaluations for applications currently in a pre-interview screen stage, so clearing permanently removes evaluations for applications that have since moved on.
3. If a sync to S3 Data Lake or Iceberg fails with a schema-evolution error, drop the affected tables and then refresh the same streams in Airbyte. For `applications`, the refresh is required: dropping the table alone doesn't reset the incremental cursor, so the next sync would write only recently updated applications.

### Update downstream queries

- `applications.archiveReason` is now an object. Replace comparisons against the string with its fields, for example `archiveReason.text` or `archiveReason.reasonType` (such as `RejectedByOrg`).
- `job_postings.publishedDate` is now a date, not a timestamp. Remove time-zone conversions and timestamp casts.
- Queries that select the removed `interviews` or `application_criteria_evaluations` columns must stop selecting them. Those values were always null; read scheduled-interview data from `interview_schedules` instead.

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
