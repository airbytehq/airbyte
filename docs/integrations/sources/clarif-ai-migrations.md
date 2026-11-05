# Clarif-ai Migration Guide

## Upgrading to 1.0.0

The `applications`, `datasets`, and `models` streams now emit `modified_at` timestamps
with six fractional digits (microsecond precision). Previously, nanosecond timestamps
could be delivered without advancing incremental state. Digits beyond microseconds
are truncated. Timestamp field names and string types, primary keys, and saved-state
structures are unchanged. Other streams are unaffected.

1. Review SQL, dbt models, dashboards, and exports that compare exact `modified_at`
   strings in these three streams. Update comparisons that require nine fractional
   digits to accept six.
2. Upgrade the connector. No configuration changes, schema refresh, or stream clear
   are required. Existing start-date and per-application state are accepted.
3. Run a sync and verify the saved state advances to the newest modification time.

Full refresh overwrite replaces rows with the current normalized output. Append
modes preserve historical rows, so old and new timestamp precision can coexist.
Append + Deduped retains the same primary keys; newly synced versions of a record
can replace older versions. Do not clear streams solely to change timestamp
precision: clearing deletes destination history that may no longer exist upstream.

The automatic upgrade does not require data-destructive remediation. Consumers
that require nanosecond precision should review the change before upgrading.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
