# QuickBooks Migration Guide

## Upgrading to 4.0.0

The config no longer has a nested credentials field: the config fields remain the same, but they are now at the root level instead of being nested inside a credentials object. This was done to fix the refresh token issue where it wasn't getting updated after 24 hours.

As of 4.1.9 this migration is automatic — configs still using the old nested `credentials` shape are lifted to the root-level shape on the next sync, and no manual action is needed. On versions 4.0.0 through 4.1.8 you had to repopulate the config fields by hand.

## Upgrading to 3.0.0

Some fields in `bills`, `credit_memos`, `items`, `refund_receipts`, and `sales_receipts` streams have been changed from `integer` to `number` to fix normalization. You may need to refresh the connection schema for those streams (skipping the reset), and running a sync. Alternatively, you can just run a reset.
