# Contributing to source-quickbooks

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

Source QuickBooks is a manifest-only (declarative YAML) connector. There is no Python code in this directory — all behavior lives in `manifest.yaml` (28 streams). Do not edit `README.md`; it is a symlink to a shared file.

## Deletion patterns

QuickBooks Online has two distinct deletion mechanisms, per the [Intuit API documentation](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api):

- **Soft deletes** apply to *list* (name list) entities: the record is marked `Active: false` and can be reactivated. It remains queryable.
- **Hard deletes** apply to *transaction* entities: the record is permanently removed and disappears from `/v3/company/<realmId>/query` results.

### Soft-deleted list entities (covered)

12 of the 28 streams query list entities and append `AND Active IN (true, false)` to their SQL-like query so soft-deleted (inactive) records are still emitted:

`accounts`, `budgets`, `classes`, `customers`, `departments`, `employees`, `items`, `payment_methods`, `tax_codes`, `tax_rates`, `terms`, `vendors`

This is the canonical pattern for any newly added list-entity stream. Practical effect: consumers must read the `Active` field to detect soft deletions — soft-deleted records are not removed from the destination.

### Hard-deleted transaction entities (not covered)

The remaining 16 streams query transaction entities:

`bill_payments`, `bills`, `credit_memos`, `deposits`, `estimates`, `invoices`, `journal_entries`, `payments`, `purchase_orders`, `purchases`, `refund_receipts`, `sales_receipts`, `tax_agencies`, `time_activities`, `transfers`, `vendor_credits`

These are hard-deleted, so a deleted record simply disappears from query results and the connector has no way to propagate the deletion today.

**Trade-off considered:** the [Change Data Capture operation](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/change-data-capture) (`GET /v3/company/<realmId>/cdc?entities=<list>&changedSince=<ts>`) returns changed entities with `status: "Deleted"` for deletions. However, it is limited to a 30-day look-back window and a 1,000-object response cap, so it cannot be the sole replication mechanism — it could only supplement the query-based streams for recent hard deletes. This is a documented trade-off, not a committed plan.

## The `airbyte_cursor` synthetic cursor

Every stream uses `incremental_sync: DatetimeBasedCursor` with:

- `cursor_field: airbyte_cursor`
- `datetime_format: "%Y-%m-%dT%H:%M:%S%z"`
- `step: P30D`, `cursor_granularity: PT0S`

The real cursor value is nested at `MetaData.LastUpdatedTime`, so each stream declares a `transformations: AddFields` entry that copies `{{ record.MetaData.LastUpdatedTime }}` into a top-level `airbyte_cursor` field. `airbyte_cursor` is also declared in each stream's inline schema, so it lands in the destination as a real column.

Any newly added stream must replicate the same AddFields + schema-property pair to stay consistent.

Requests window on the underlying field, e.g.:

```sql
SELECT * FROM <Entity> WHERE Metadata.LastUpdatedTime > '<start>' AND Metadata.LastUpdatedTime <= '<end>' ORDER BY Metadata.LastUpdatedTime ASC STARTPOSITION <n> MAXRESULTS <page_size>
```

## Error mappings

`manifest.yaml` currently contains no `error_handler`, `HttpResponseFilter`, or retry configuration — the connector relies entirely on CDK default error handling. Adding error handling and Intuit fault-code mapping is tracked in [airbyte-internal-issues#17093](https://github.com/airbytehq/airbyte-internal-issues/issues/17093).

## Config shape (4.0.0 breaking change)

In 4.0.0 the nested `credentials` object was flattened to root level, and users had to repopulate config fields. The current spec requires these root-level fields:

`client_id`, `client_secret`, `refresh_token`, `access_token`, `token_expiry_date`, `realm_id`, `start_date`, `sandbox`

No automatic config migration ships with the connector (tracked in [airbyte-internal-issues#17099](https://github.com/airbytehq/airbyte-internal-issues/issues/17099)). Any CI/test secret must therefore be in the root-level shape (tracked in [airbyte-internal-issues#17087](https://github.com/airbytehq/airbyte-internal-issues/issues/17087)).
