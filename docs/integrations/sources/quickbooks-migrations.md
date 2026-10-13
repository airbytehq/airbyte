# QuickBooks Migration Guide

## Upgrading to 5.0.0

From version 4.2.0 onward, Airbyte's platform replaces `client_id` and `client_secret` with Airbyte's app credentials whenever `auth_type` is `oauth2.0`. Existing sources use their own Intuit app, so every source must be reconfigured for 5.0.0.

- To authorize through Airbyte's QuickBooks app, select `oauth2.0` and click **Authenticate your QuickBooks account**. This option supports production companies only.
- To use your own Intuit app, select `client_credentials` and enter its Client ID, Client Secret, Refresh Token, and Realm ID.

Sandbox companies require `client_credentials` with your app's development keys and **Sandbox** turned on. Airbyte's app can only access production companies.

## Upgrading to 4.0.0

The config no longer has a nested credentials field, while the config fields remain the same, they are now at the root level instead of being nested inside a credentials object. This is done to fix the refresh token issue where it wasn't getting updated after 24 hours.

4.0.0 shipped without a config migration, so connections created before it had to have their config fields repopulated by hand. Since 4.2.0 the connector migrates a nested `credentials` config to the root-level fields on its own and persists the result, so no manual repopulation is needed.

## Upgrading to 3.0.0

Some fields in `bills`, `credit_memos`, `items`, `refund_receipts`, and `sales_receipts` streams have been changed from `integer` to `number` to fix normalization. You may need to refresh the connection schema for those streams (skipping the reset), and running a sync. Alternatively, you can just run a reset.
