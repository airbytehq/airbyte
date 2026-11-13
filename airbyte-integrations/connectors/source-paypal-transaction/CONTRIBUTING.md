# Contributing to source-paypal-transaction

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The PayPal API supports date-based filtering on transaction search (`start_date`/`end_date`) and balance endpoints, which the connector already uses for incremental streams. The remaining FR parent streams are `list_products` (catalog products listing) and `search_invoices` (invoice search). The products endpoint does not support date filtering. The invoices search endpoint supports date ranges but the connector currently uses full-refresh.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| balances | medium | top-level parent | as_of_time | as_of_time | incremental |  |
| list_disputes | medium | top-level parent | updated_time_cut | updated_time_cut | incremental |  |
| list_payments | medium | top-level parent | update_time | update_time | incremental |  |
| list_products | small | top-level parent | none | none | deferred_no_api_support | Catalog products; no date filter on list endpoint |
| search_invoices | medium | top-level parent | none | created_at_only | deferred_no_api_support | Supports `invoice_date_range` but invoices are mutable (payments, refunds) |
| transactions | medium | top-level parent | transaction_updated_date | transaction_updated_date | incremental |  |
| show_product_details | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `list_products` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Created-at only (1 streams):** `search_invoices` — these endpoints support `created` filtering but the resources are mutable, making `created_at`-only filtering insufficient for true incremental sync.
- **Child streams (1 streams):** `show_product_details` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
