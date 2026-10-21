import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Uptick Migration Guide

## Upgrading to 3.0.0

Version 3.0.0 changes the `tracking_categories` schema on two streams, removes unused legacy configuration fields, and rejects an empty or whitespace-only `base_url`.

### What changed

The `costcentres.tracking_categories` and `products.tracking_categories` fields change from an object to an array of objects, matching what the Uptick API returns. Destinations with typed columns will see the column type change.

Earlier versions declared `tracking_categories` as an object while the API returned an array. Destinations on the current bulk-load CDK (for example BigQuery, Snowflake, Postgres, MSSQL, and S3 Data Lake) wrote `null` for it and recorded the change in `_airbyte_meta.changes`. From 3.0.0, the values arrive as arrays.

The connector removes `end_date` and `start_date` automatically. It removes the legacy `oauth_access_token`, `oauth_token_expiry_date`, and `client_refresh_token` fields once the configuration has `credentials.auth_type` set, which the connector adds automatically for existing username and password configurations.

The connector rejects an empty or whitespace-only `base_url`. Existing working configurations are unaffected.

### Who is affected

This change affects users who sync `costcentres` or `products` and have destinations with typed columns, or downstream queries, dashboards, and transformations that expect `tracking_categories` to be an object. S3 Data Lake and other Iceberg destinations cannot change the column type in place, so those streams must be cleared or refreshed after the upgrade. Connections with an empty or whitespace-only `base_url` must also be updated to use a valid workspace URL.

### Required actions

Before upgrading, update downstream queries, dashboards, and transformations that read `tracking_categories` on `costcentres` or `products` so they treat it as an array of objects. It can also be an empty array.

After upgrading to version 3.0.0:

1. Refresh the source schema for connections syncing `costcentres` or `products`.
2. Clear the `costcentres` and `products` streams, or run **Refresh (remove records)** on them, so rows synced before 3.0.0 get their `tracking_categories` values:
   - **Required** for S3 Data Lake and other Iceberg destinations, unless the stream uses **Full refresh | Overwrite**. These destinations can't change the column from a string to a list in place, so the next sync fails until the stream is cleared or refreshed.
   - **Recommended** for other destinations with typed columns. Rows written before 3.0.0 may have a `null` `tracking_categories`, and incremental syncs only update rows that change in Uptick.
   - Not needed for streams that use **Full refresh | Overwrite**, because every sync rebuilds them.

   A clear doesn't lose history. The connector re-reads every cost centre and product from Uptick, including deleted ones.
3. Run a sync and verify downstream models against the updated schemas.

No action is needed for the removed legacy configuration fields or for existing valid `base_url` values.

## Upgrading to 2.0.0

Version 2.0.0 upgrades the connector from Uptick API v2.15 to v2.16, corrects the types of several fields, and makes the `majorservices` stream full refresh only.

### What changed

The following fields have been removed, because Uptick API v2.16 no longer exposes them:

- `properties.access_signaturereq`: use `client_signature_required`, which the stream already includes.
- `servicetasks.from_stock`: a service task that came from stock has no `purchaseorderlineitem_id`.

The following fields change type, to match what the Uptick API returns:

- `properties.address`, `properties.coords` and `branches.business_hours`: string to object.
- `servicequotes.product_subtotal`: string to number.

The `majorservices` stream no longer supports incremental sync. Its endpoint has no `updated` timestamp, so incremental syncs re-read every record and, in append mode, duplicated every row on each sync. The stream also drops its `created` and `updated` columns. The Uptick `MajorService` model has no `created` or `updated` field, so the API never returned them and these columns were always `null`.

From this version, the `servicegroups` and `accreditationtypes` streams filter on `updated` server-side, so incremental syncs of these streams fetch only changed rows. This needs no action.

### Who is affected

This change affects users who sync the `properties`, `servicetasks`, `branches`, `servicequotes` or `majorservices` streams and have downstream queries, dashboards, transformations, or destination schemas that reference the changed fields, or who sync `majorservices` in incremental mode.

### Required actions

Before upgrading to version 2.0.0:

1. Update downstream queries, dashboards, and transformations to remove references to the deleted fields, and to read the changed fields as objects or numbers.

After upgrading:

1. Refresh the source schema for each affected connection.
2. Switch the `majorservices` stream to a full refresh sync mode. **Full refresh | Overwrite** is recommended: the next sync rebuilds the table and removes the rows that earlier incremental syncs duplicated, so you don't need to clear it. If you choose **Full refresh | Append**, clear the stream once to remove the old duplicates, and note that every later sync appends another full copy of the table. Connections that used **Incremental | Append + Deduped** have no duplicate rows and only need the sync mode change. A clear doesn't lose history: the stream re-reads every major service from Uptick, including deleted ones.
3. Run a sync and verify downstream models against the updated schemas.

## Upgrading to 1.0.0

Version 1.0.0 upgrades the connector from Uptick API v2.14 to v2.15. Uptick API v2.15 no longer exposes several fields that were present in earlier API responses, so this release removes those fields from the connector schema.

### What changed

The following fields have been removed:

- `branches.fax`
- `defectquotelineitems.product_type`
- `servicetasks.due`
- `servicetasks.is_majorservice`
- `tasksessions.submitted`
- `tasksessions.is_approved`
- `tasksessions.is_submitted`

For the `tasksessions` stream, use `submitted_at` instead of `submitted`. To replace the removed boolean fields, treat a non-null `submitted_at` value as submitted and a non-null `approved_at` value as approved. The other removed fields do not have direct replacements in the connector.

### Who is affected

This change affects users who sync the `branches`, `defectquotelineitems`, `servicetasks`, or `tasksessions` streams and have downstream queries, dashboards, transformations, or destination schemas that reference the removed fields.

### Required actions

Before upgrading to version 1.0.0:

1. Update downstream queries, dashboards, and transformations to remove references to the deleted fields or use the `tasksessions` replacements described above.

After upgrading:

1. Refresh the source schema for each affected connection.
2. Review and save the affected connection schemas so the removed fields are no longer selected.
3. Run a sync and verify downstream models against the updated schemas.

## Upgrading to 0.4.0

This release introduces breaking changes that remove unused fields from the connector schema.

### What changed

- The `assets` stream no longer includes the `floorplan_location_id` field.
- The `tasksessions` stream no longer includes `hours`, `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished`. These computed fields were removed to reduce server load.

### Who is affected

This change affects users who sync the `assets` or `tasksessions` streams and have downstream queries, dashboards, or transformations that reference the removed fields.

### Required actions

After upgrading to version 0.4.0:

1. **Update downstream queries and dashboards** that reference removed fields:
   - For `assets`: Remove references to `floorplan_location_id`.
   - For `tasksessions`: Replace `hours` with `duration_hours` if you were using it. Remove references to `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished`.

## Connector upgrade guide

<MigrationGuide />
