# Zoho Books Migration Guide

## Upgrading to 1.0.0

This release changes the incremental cursor for several financial streams from the record `date` to `last_modified_time`.

### What changed

The following streams now use `last_modified_time` for incremental syncs:

- `invoices`
- `expenses`
- `creditnotes`
- `customer_payments`
- `purchase_orders`
- `sales_orders`

Previously, these streams used `date`, which only tracked the record date and could miss later edits such as status changes, payments, and other updates.

### Required actions

After upgrading to version 1.0.0:

1. **Refresh your source schema** in the Airbyte UI.
2. **Reset the affected streams** listed above so Airbyte can re-sync data and rebuild state with the new cursor.
3. **Review downstream models or dashboards** that rely on incremental freshness for these streams.

If you do not sync any of the affected streams incrementally, no action is required.
