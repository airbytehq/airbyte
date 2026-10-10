# Stripe Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 7.0.0

Version 7.0.0 changes the `id` values that incremental syncs of the `invoice_line_items` stream write for Stripe accounts whose default API version is older than `2019-12-03`. `id` is this stream's primary key, so on those accounts, rows written by earlier versions don't match rows written by 7.0.0. Most Stripe accounts use a newer default API version and aren't affected.

### What changed

After the first sync, incremental syncs of `invoice_line_items` read line items from the Stripe Events API. Stripe renders each event in the account's default API version at the time the event was created, whatever API version the connector requests. Before `2019-12-03`, Stripe used legacy invoice line item IDs:

- `ii_...`: the ID of the invoice item behind the line.
- `sub_...`: the ID of the subscription behind the line. It repeats on every renewal invoice for that subscription.
- `su_...`: also a subscription ID, used by some older subscriptions. Like `sub_...`, it repeats on every renewal invoice for that subscription.
- `sli_...`: a subscription line item ID used by API versions from 2018 and 2019.

Full refresh syncs read the same line items from the Invoices endpoints and get Stripe's current `il_...` IDs. Before 7.0.0, one connection could therefore write the same line item under two different IDs. In a deduplicated destination, each renewal of a `sub_...` or `su_...` line also replaced the previous renewal's row.

In 7.0.0, incremental syncs use the current `il_...` ID that Stripe includes in legacy event payloads, so incremental and full refresh syncs write the same IDs. On legacy subscription lines whose ID was the subscription ID, the `subscription` field is now filled with that subscription ID. No other streams, fields, or sync modes change.

### Who is affected

You're affected only if both of these are true:

- You sync `invoice_line_items` with an incremental sync mode.
- Your Stripe account's default API version is older than `2019-12-03`. Workbench in the Stripe Dashboard shows your account's default API version.

To check your destination, run this query, replacing `<schema>` with your destination schema:

```sql
SELECT COUNT(*) FROM <schema>.invoice_line_items WHERE SUBSTR(id, 1, 3) <> 'il_';
```

If the count is `0`, you don't need to do anything. The upgrade doesn't change your data. Rely on the count rather than your account's current default API version: events keep the API version that was your default when Stripe created them, so an account that has since upgraded its API version can still have legacy rows from earlier syncs.

### Migration steps

If the query returns a count greater than zero:

1. Upgrade the connector to 7.0.0.
2. [Refresh the `invoice_line_items` stream and remove records](/platform/operator-guides/refreshes).

You must remove records. The legacy rows have a different primary key from the new `il_...` rows, so refreshing and retaining records leaves the legacy rows in your destination alongside the new ones.

Refreshing and removing records deletes this stream's existing data in your destination before syncing it again. The refreshed stream is rebuilt from the Invoices endpoints, not from the 30-day Events API window, but only for invoices **created** on or after your configured start date. The refresh doesn't recreate:

- Line items of invoices created before your start date. Earlier incremental syncs picked these up whenever such an invoice changed. To keep them, set the start date on or before your oldest invoice's creation date before you refresh. Changing the start date also affects other streams.
- Rows that recorded deleted draft invoices (`is_deleted` is `true`).
- In an Incremental | Append destination, the earlier versions of each line item. The refresh writes only each line item's current state.

Back up the `invoice_line_items` table before you refresh if you need any of these rows or the legacy IDs.

### If you don't refresh

Upgrading to 7.0.0 stops new legacy IDs from being written, but rows that earlier versions wrote stay in your destination until you refresh the stream:

- Line items synced incrementally before the upgrade keep their legacy ID, and the same line items appear again under their `il_...` ID when they're next synced. Counts and sums over `invoice_line_items` can include these line items twice.
- In a deduplicated destination, older renewal lines of a subscription that were replaced under a shared `sub_...` or `su_...` ID stay missing.

### Downstream changes

Queries, models, and dashboards that join or filter on `invoice_line_items.id` using legacy `ii_...`, `sub_...`, `su_...`, or `sli_...` values must use `il_...` IDs instead. To relate a subscription line to its subscription, use the `subscription` field rather than the line's `id`.

For general upgrade steps, see the [connector upgrade guide](#connector-upgrade-guide).

## Upgrading to 6.0.0

Version 6.0.0 fixes a bug where the `invoice_line_items` and `subscription_items` incremental streams emitted only one record per Stripe event instead of correctly expanding nested line items. An event containing N line items previously produced 1 record; it now produces N records.

### What changed

We changed how records are extracted from the API response for the `invoice_line_items` and `subscription_items` streams to ensure nested data is properly treated as individual records.

#### Example: `invoice_line_items`

**Before (5.x):** A single Stripe event with an invoice containing 3 line items produced 1 flattened record:

```json
{
  "id": "evt_1234",
  "type": "invoice.updated",
  "data": {
    "object": {
      "id": "in_abc",
      "lines": {
        "data": [
          {"id": "il_1", "amount": 1000},
          {"id": "il_2", "amount": 2000},
          {"id": "il_3", "amount": 500}
        ]
      }
    }
  }
}
```

This event emitted **1 record** containing the top-level event fields. The nested line items inside `data.object.lines.data` were lost.

**After (6.0.0):** The same event now emits **3 records**, 1 per line item:

```json
{"id": "il_1", "amount": 1000, "invoice_id": "in_abc", "invoice_updated": 1712600000}
{"id": "il_2", "amount": 2000, "invoice_id": "in_abc", "invoice_updated": 1712600000}
{"id": "il_3", "amount": 500, "invoice_id": "in_abc", "invoice_updated": 1712600000}
```

The same change applies to `subscription_items`, which expands items from `data.object.items.data`.

### Who is affected

Users syncing the `invoice_line_items` or `subscription_items` streams in incremental mode. Previously synced data for these streams may be incomplete due to the bug.

### Migration steps

After upgrading, you can choose to either leave your syncs as-is or run a full refresh to recapture the correct values for impacted fields.

**Option 1: Leave syncs alone.** Future incremental syncs will emit records correctly. Historical data already in your destination will remain incomplete, but no action is required.

**Option 2: Run a full refresh.** A full refresh will recapture the correct values for all records in the impacted streams. If you choose this option, decide between:

- **Full Refresh and Retain records:** Keeps existing data in your destination and layers the refreshed data on top. This is the safer option for most users.
- **Full Refresh and Clear:** Replaces all existing data in the destination for these streams. **Use caution:** because the Stripe Events API only retains events for the last 30 days, clearing will cause you to lose all updates to event-based streams in your destination that are older than 30 days. See the [Stripe API event retention limitation](/integrations/sources/stripe#limitations--troubleshooting) for more details.

:::tip
If the 30-day retention window is a concern, consider making a backup of your currently synced data in a separate table in your destination before clearing the stream. Once the backup is complete, you can safely run a Full Refresh and Clear without losing historical data.
:::

### Connector upgrade guide

<MigrationGuide />

### Upgrading to 5.6.0

The `Payment Methods` stream previously sync data from Treasury flows. This version will now provide data about customers' payment methods.

We bumped this in a minor version because we didn't want to pause all connection, but still want to document the process of moving to this latest version.

### Summary of changes:

- The stream `Payment Methods` will now provide data about customers' payment methods.
- The stream `Payment Methods` now incrementally syncs using the `events` endpoint.
- `customer` field type will be changed from `object` to `string`.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).



## Upgrading to 5.4.0

The `Refunds` stream previously did not sync incrementally correctly. Incremental syncs are now resolved, and the `Refunds` stream now receives the correct updates using the `events` endpoint. This version resolves incremental sync issues with the `Refunds` stream.

### Summary of changes: 

- The stream `Refunds` cursor changed from the field `created` to `updated` when syncing incrementally.
- The stream `Refunds` now incrementally syncs using the `events` endpoint.

### Migration Steps

1. Upgrade the Stripe connector by pressing the upgrade button and following the instructions on the screen.

:::info
The following migration steps are relevant for those who would like to sync `Refunds` incrementally. These migration steps can be skipped if you prefer to sync using `Full Refresh`. 
:::

The stream `Refunds` will need to be synced historically again to ensure the connection continues syncing smoothly. If available for your destination, we recommend initiating a `Refresh` for the stream, which will pull in all historical data for the stream without removing the existing data first and update your destination with all data once complete. To initiate a `Refresh`:

1. Navigate to the connection's `Schema` tab. Navigate to the `Refunds` stream.
2. Update the `Refunds` stream to use the `Incremental | Append + Dedup` sync mode. This ensures your data will sync correctly and capture all updates efficiently.
3. If your stream already has a sync mode of either `Incremental | Append + Dedup` or `Incremental | Append`, simply update the cursor from `created_at` to `updated_at`.
4. Save the connection.
5. Review the prompt to `Refresh` the `Refunds` stream. Select `Refresh and retain records` to ensure any data no longer found in Stripe is retained in your destination.
6. Confirm the modal to save the connection and initiate a `Refresh`. This will start to pull in all historical data for the stream.

:::note
If you are using a destination that does not support the `Refresh` feature, you will need to [Clear](/platform/operator-guides/clear) your stream. This will remove the data from the destination for just that stream. You will then need to sync the connection again in order to sync all data again for that stream.
:::

## Upgrading to 5.0.0

This change fixes multiple incremental sync issues with the `Refunds`, `Checkout Sessions` and `Checkout Sessions Line Items` streams:

- `Refunds` stream was not syncing data in the incremental sync mode. Cursor field has been updated to "created" to allow for incremental syncs. Because of the changed cursor field of the `Refunds` stream, incremental syncs will not reflect every update of the records that have been previously replicated. Only newly created records will be synced. To always have the up-to-date data, users are encouraged to make use of the lookback window.
- `CheckoutSessions` stream had been missing data for one day when using the incremental sync mode after a reset; this has been resolved.
- `CheckoutSessionsLineItems` previously had potential data loss. It has been updated to use a new cursor field `checkout_session_updated`.
- Incremental streams with the `created` cursor had been duplicating some data; this has been fixed.

Stream schema update is a breaking change as well as changing the cursor field for the `Refunds` and the `CheckoutSessionsLineItems` stream. A schema refresh and data reset of all effected streams is required after the update is applied.

Also, this update affects three more streams: `Invoices`, `Subscriptions`, `SubscriptionSchedule`. Schemas are changed in this update so that the declared data types would match the actual data.

Stream schema update is a breaking change as well as changing the cursor field for the `Refunds` and the `CheckoutSessionsLineItems` stream. A schema refresh and data reset of all effected streams is required after the update is applied.
Because of the changed cursor field of the `Refunds` stream, incremental syncs will not reflect every update of the records that have been previously replicated. Only newly created records will be synced. To always have the up-to-date data, users are encouraged to make use of the lookback window.

## Upgrading to 4.0.0

A major update of most streams to support event-based incremental sync mode. This allows the connector to pull not only the newly created data since the last sync, but the modified data as well.
A schema refresh is required for the connector to use the new cursor format.
