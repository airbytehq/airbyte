# Stripe Migration Guide

## Upgrading to 5.4.0

The `Refunds` stream previously did not sync incrementally correctly. Incremental syncs are now resolved, and the `Refunds` stream now receives the correct updates using the `events` endpoint. This version resolves incremental sync issues with the `Refunds` stream.

### Summary of changes: 

- The stream `Refunds` cursor changed from the field `created` to `updated`.
- The stream `Refunds` incrementally syncs using the `events` endpoint.

### Migration Steps

The stream `Refunds` will need to be synced historically again to ensure the connection continues syncing smoothly. If available for your destination, we recommend doing a `Refresh` for the stream. To [refresh](/operator-guides/refreshes) a single stream,
1. Navigate to a Connection's status page
2. Click the three grey dots next to `Refunds`
3. Select "Refresh data".
4. Select "Refresh and retain records" to ensure any data no longer found in Stripe is retained in your destination.

This will start to pull in all historical data for the stream without removing the existing data first and update your destination with all data once complete. 

If you are using a destination that does not support the `Refresh` feature, you will need to [Clear](/operator-guides/clear) your stream before initiating a new sync. To `Clear` a single stream,
1. Navigate to a Connection's status page
2. Click the three grey dots next to `Refunds`
3. Select "Clear data".

This will remove the data from the destination for just that stream. You will then need to sync the connection again in order to sync all data again for that stream.

:::tip
The `Refunds` stream previously did not sync using the `events` endpoint, so it retained records beyond 30 days. The `Refunds` stream now uses the `events` endpoint, which limits the results synced to the last 30 days. We recommend retaining a version of your historical data during this process to ensure no data loss occurs.
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
