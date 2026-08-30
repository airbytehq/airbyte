# QuickBooks Migration Guide

## Upgrading to 4.0.0

The config no longer has a nested credentials field, while the config fields remain the same, they are now at the root level instead of being nested inside a credentials object. You will need to repopulate the config fields to make the connector work again. This is done to fix the refresh token issue where it wasn't getting updated after 24 hours.

As of 4.1.9, configs that still use the old nested `credentials` shape are migrated automatically. You do not need to repopulate the config fields manually.

## Upgrading to 3.0.0

Some fields in `bills`, `credit_memos`, `items`, `refund_receipts`, and `sales_receipts` streams have been changed from `integer` to `number` to fix normalization. You may need to refresh the connection schema for those streams (skipping the reset), and running a sync. Alternatively, you can just run a reset.
