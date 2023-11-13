# Stripe Migration Guide

## Upgrading to 5.0.0

This change fixes multiple issues for the `Refunds`, `Checkout Sessions` and `Checkout Sessions Line Items` streams:

 - `CheckoutSessions` stream missing data for one day when using the incremental sync mode after a reset
 - `Refunds` stream not syncing data in the incremental sync mode
 - `CheckoutSessionsLineItems` potential data loss
 - Incremental streams with the `created` cursor duplicating some data

Some changes here are breaking - the cursor field is changed for the `Refunds` and the `CheckoutSessionsLineItems` stream. A schema refresh and data reset of all effected streams is required after the update is applied.
Because of the changed cursor field of the `Refunds` stream, incremental syncs will not reflect every update of the records that have been previously replicated. Only newly created records will be synced. To always have the up-to-date data, users are encouraged to make use of the lookback window.

## Upgrading to 4.0.0

A major update of most streams to support event-based incremental sync mode. This allows the connector to pull not only the newly created data since the last sync, but the modified data as well.
A schema refresh is required for the connector to use the new cursor format.