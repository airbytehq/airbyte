# Pennylane Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 moves the connector from the deprecated Pennylane API v1 to API v2. Existing data is not compatible with the new version, so you need to reset your streams after upgrading.

### What changed

- **API token:** API v2 uses more granular scopes. Create a token with read access to the resources you sync.
- **IDs:** all streams use API v2 internal IDs as `id`. Existing `id` values change, except where they already matched `v2_id`.
  - For invoices and suppliers, the previous `v2_id` matches the new `id`.
  - For customers and products, the previous `source_id` matches the new `external_reference`.
- **Stream names:** `customer_estimates` is replaced by `quotes`, and `plan_items` by `ledger_accounts`.
- **Nested data:** API v2 no longer embeds nested collections in invoices. Use these streams instead of the former fields:
  - `line_items` is now `customer_invoice_lines` and `supplier_invoice_lines`.
  - `categories`, `matched_transactions` and `payments` are now `customer_invoice_*` and `supplier_invoice_*` streams.
- **Archived records:** API v2 returns archived records, which API v1 did not list. Filter on `archived_at` to exclude them.
- **Credit notes:** customer credit notes are now separate `customer_invoices` records. Use `credited_invoice` to link them to their invoice. They are no longer nested in `credit_notes`.
- **Field names:** several fields were renamed, for example `is_draft` to `draft`, and `remaining_amount` to `remaining_amount_with_tax` and `remaining_amount_without_tax`.

### Steps

1. Create a Pennylane API v2 token.
2. Update your source with the new token, and upgrade the connector to 1.0.0.
3. Refresh the source schema and select the streams you need.
4. Reset the connection's streams and run a sync.
5. Update anything downstream to use the new IDs, stream names and fields.
