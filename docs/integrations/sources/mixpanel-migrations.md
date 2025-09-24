import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Mixpanel Migration Guide

## Upgrading to 3.0.0

In this release, we introduce breaking change for `CohortMembers` stream:

- State is changed to per-partition format.
- Key is changed to a unique key (based on `distinct_id` and `cohort_id` fields). The previous key was not unique and didn't support the possibility for user be in multiple cohorts.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

:::note
To add start date filtering for the `Cohorts`, `CohortMembers`, and `Engage` streams, the default retrieval range has been updated from all existing records to only include records created within the past year if start date not provided.
:::

## Connector upgrade guide

<MigrationGuide />

## Upgrading to 2.0.0

In this release, the default primary key for stream Export has been deleted, allowing users to select the key that best fits their data. Refreshing the source schema and resetting affected streams is necessary only if new primary keys are to be applied following the upgrade.

## Upgrading to 1.0.0

In this release, the datetime field of stream engage has had its type changed from date-time to string due to inconsistent data from Mixpanel. Additionally, the primary key for stream export has been fixed to uniquely identify records. Users will need to refresh the source schema and reset affected streams after upgrading.
