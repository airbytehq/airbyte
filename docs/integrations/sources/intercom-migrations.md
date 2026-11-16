import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Intercom Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 changes the `company_segments` stream so each record says which company the segment is attached to.

### What changes

- A new `company_id` field holds the Intercom ID of the company, the same value as `id` in the `companies` stream.
- The primary key changes from `id` to `[company_id, id]`.

### Why

Intercom's [List attached segments for companies](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/companies/listattachedsegmentsforcompanies) endpoint returns the segment objects only, with no reference to the company. Before 1.0.0 the stream emitted the same segment once for every company in it, with no way to tell the rows apart, and deduplicated destinations kept a single row per segment.

### Who is affected

Connections that sync `company_segments`. Connections that don't sync it need no action.

- **Full Refresh | Overwrite**: the next sync rebuilds the table with the new column and key. No action.
- **Full Refresh | Append**: every sync emits all memberships again, so new rows carry `company_id` from the first sync after the upgrade; rows written before the upgrade have it empty. No action. Filter on `company_id is not null` downstream.
- **Incremental | Append**: rows written before the upgrade have `company_id` empty, and the saved state carries over, so later syncs only emit memberships of companies and segments updated since the last sync. Refresh the stream as described below, keeping the records, then filter on `company_id is not null` downstream.
- **Incremental | Append + Deduped**: rows written before the upgrade are keyed by `id` alone and stay next to the new rows. Refresh the stream as described below.

### Upgrade steps

1. Upgrade the Intercom source to 1.0.0.
2. Refresh the source schema for each affected connection and review the detected changes before saving.
3. If `company_segments` uses an incremental sync mode, refresh only that stream:
   - **Incremental | Append + Deduped**: **Refresh stream** → **Refresh stream and remove records**. The old rows have no `company_id`, so removing them loses nothing a re-sync can't rebuild. Intercom only returns current memberships, so memberships that ended before the refresh don't come back.
   - **Incremental | Append**: **Refresh stream** → **Refresh stream and retain records**. The refresh clears the saved state, so the next sync reads the stream from Start Date again and writes rows with `company_id`. The old rows stay, with `company_id` empty.
4. Update downstream queries that join or deduplicate `company_segments` on `id` alone: use `(company_id, id)`, and join to `companies.id`, not `companies.company_id`.

## Connector upgrade guide

<MigrationGuide />
