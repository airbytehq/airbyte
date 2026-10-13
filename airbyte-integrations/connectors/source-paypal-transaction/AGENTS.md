> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-paypal-transaction

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Oversized Transaction Search Windows

PayPal's transaction search rejects a query whose result set exceeds 10,000 transactions with HTTP 400 `RESULTSET_TOO_LARGE` and returns no page, so pagination cannot make progress and the cursor never advances. The `transactions` stream handles this declaratively via the CDK's `request_window_splitting` retriever field: a `SPLIT_REQUEST_WINDOW` `HttpResponseFilter` (matching `response.get('name') == 'RESULTSET_TOO_LARGE'`) tells the retriever to re-read the rejected window as halves, using the stream's own `DatetimeBasedCursor` (boundary field names, format, and `cursor_granularity: PT1S` are read directly from `incremental_sync` - there is no separate config to keep in sync). No custom retriever or error handler is needed; `components.py` only defines `PayPalOauth2Authenticator` for auth. The CDK stops after 10 halvings (about 9m49s at the default `time_window: 7`, 83s at `time_window: 1`) or at the one-second `cursor_granularity`, whichever comes first. If the window is still rejected at that point, the stream fails with a `transient_error`; lowering `time_window` lets the split reach smaller windows. The mechanism was added in airbytehq/airbyte-python-cdk#1171 and replaced the custom `DateWindowSplittingRetriever`/`ResultSetTooLargeErrorHandler` pair.

## Disputes 180-Day Lookback Floor

PayPal's Customer Disputes API requires `update_time_after` to be within the last 180 days and rejects anything older with HTTP 400 `INVALID_REQUEST` / `INVALID_DATE_RANGE`. The `list_disputes` start boundary is resolved once when the stream is built and reused for every request, so a boundary of exactly `day_delta(-180)` is already out of range when the first request lands. The stream's `start_datetime` therefore carries a `min_datetime` floor of `now_utc() - P179D`, which clamps both the default start and a user-supplied `dispute_start_date` near the boundary. A stored cursor older than the floor is also raised to it by the concurrent cursor. Do not move this floor back to 180 days.

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
