# Stripe Migration Guide

## Upgrading to 5.0.0

A major update affects three streams: `Invoices`, `Subscriptions`, `SubscriptionSchedule`. Schemas are changed in this update so that the declared data types would match the actual data.
If you use at least one of the mentioned streams, a schema refresh is required for the connector to apply changes.

## Upgrading to 4.0.0

A major update of most streams to support event-based incremental sync mode. This allows the connector to pull not only the newly created data since the last sync, but the modified data as well.
A schema refresh is required for the connector to use the new cursor format.