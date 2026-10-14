# QuickBooks Migration Guide

## Upgrading to 5.0.0

In 5.0.0, the authentication fields move under `credentials`. No config migration runs, so each existing source must be reconfigured; its current configuration will fail until then.

- To authorize through Airbyte's QuickBooks app, choose **Authenticate via QuickBooks (Airbyte app)** and click **Authenticate your QuickBooks account**. This option supports production companies only.
- To use your own Intuit app, choose **Use your own Intuit app** and re-enter its Client ID, Client Secret, Refresh Token, and Realm ID.

Sandbox companies require **Use your own Intuit app** with your app's development keys and **Sandbox** turned on under that option.

## Upgrading to 4.0.0

The config no longer has a nested credentials field, while the config fields remain the same, they are now at the root level instead of being nested inside a credentials object. This is done to fix the refresh token issue where it wasn't getting updated after 24 hours.

4.0.0 shipped without a config migration, so connections created before it had to have their config fields repopulated by hand. Versions 4.2.0 through 4.x migrate a nested `credentials` config to root-level fields and persist the result. This migration is removed in 5.0.0; reconfigure each source as described above.

## Upgrading to 3.0.0

Some fields in `bills`, `credit_memos`, `items`, `refund_receipts`, and `sales_receipts` streams have been changed from `integer` to `number` to fix normalization. You may need to refresh the connection schema for those streams (skipping the reset), and running a sync. Alternatively, you can just run a reset.
