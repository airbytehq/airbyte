# Stripe Migration Guide

###  Upgrading to 5.6.0

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

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).



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
If you are using a destination that does not support the `Refresh` feature, you will need to [Clear](/operator-guides/clear) your stream. This will remove the data from the destination for just that stream. You will then need to sync the connection again in order to sync all data again for that stream.
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
