# QuickBooks Migration Guide

## Upgrading to 3.0.0

Some fields in `bills`, `credit_memos`, `items`, `refund_receipts`, and `sales_receipts` streams have been changed from `integer` to `number` to fix normalization. You may need to refresh the connection schema for those streams (skipping the reset), and running a sync. Alternatively, you can just run a reset.
