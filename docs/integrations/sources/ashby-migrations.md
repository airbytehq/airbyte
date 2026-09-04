import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Ashby Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 removes twelve columns from the `interviews` stream that Ashby's API never populated. This is a breaking change for connections that sync the `interviews` stream.

### What changed

The following columns are removed from the `interviews` stream:

- `applicationId`
- `interviewScheduleId`
- `interviewStageId`
- `status`
- `createdAt`
- `updatedAt`
- `cancelledAt`
- `startTime`
- `endTime`
- `feedbackLink`
- `interviewerUserIds`
- `meetingLink`

No data is lost. Every removed column was always null.

### Why this changed

The `interviews` stream reads Ashby's [`/interview.list`](https://developers.ashbyhq.com/reference/interviewlist) endpoint, which returns interview *definitions*: the reusable interview templates configured on a job. The removed columns describe a *scheduled* interview, which that endpoint never returns, so they were emitted as null on every record. Version 1.2.0 declared the fields the endpoint actually returns but left these null columns in place to keep that release non-breaking. This release removes them.

Scheduling data is available in the `interview_schedules` stream: `applicationId`, `interviewStageId`, `status`, `createdAt`, and `updatedAt` are top-level fields on each schedule, and `startTime`, `endTime`, `feedbackLink`, `interviewerUserIds`, `meetingLink`, and `interviewScheduleId` are on the objects in its `interviewEvents` array. There is no direct replacement for `cancelledAt`; Ashby represents cancellation through the schedule's `status` value instead.

### Who is affected

This change affects connections that sync the `interviews` stream. All other streams are unchanged. If you built downstream models or dashboards on any of the removed columns, they reference permanently null values and should be repointed at `interview_schedules`.

### Required actions

1. Refresh the source schema for the `interviews` stream and save the connection.
2. On data-lake destinations such as S3 Data Lake and Iceberg, refresh the `interviews` stream. If a sync fails with a schema-evolution error, drop and recreate the destination table for that stream.

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
