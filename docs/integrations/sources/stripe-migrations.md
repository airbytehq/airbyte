# Stripe Migration Guide

## Upgrading to 5.4.0

This change fixes incremental sync issues with the `Refunds` stream:

- Stream cursor has changed from `created` to `updated`.

The `Reset` for the affected stream `Refunds` is required. It's safe to do, since before this update the `Refunds` stream didn't use the `events` endpoint that have `30 Days data retention` period.

Because of the changed cursor field of the `Refunds` stream, incremental syncs are now fixed and the stream receives the updates using the `events` endpoint.

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
