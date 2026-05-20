# Contributing to source-chargebee

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Chargebee API supports `updated_at` filtering via `updated_at[after]` parameter on most entity list endpoints (subscriptions, customers, invoices, etc.), which the connector already uses for 23 incremental streams. The 4 remaining streams are children partitioned via `SubstreamPartitionRouter`. No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| addon | medium | top-level parent | updated_at | updated_at | incremental |  |
| comment | medium | top-level parent | created_at | created_at | incremental |  |
| coupon | medium | top-level parent | updated_at | updated_at | incremental |  |
| credit_note | medium | top-level parent | updated_at | updated_at | incremental |  |
| customer | medium | top-level parent | updated_at | updated_at | incremental |  |
| differential_price | medium | top-level parent | updated_at | updated_at | incremental |  |
| event | medium | top-level parent | occurred_at | occurred_at | incremental |  |
| gift | medium | top-level parent | updated_at | updated_at | incremental |  |
| hosted_page | medium | top-level parent | updated_at | updated_at | incremental |  |
| invoice | medium | top-level parent | updated_at | updated_at | incremental |  |
| item | medium | top-level parent | updated_at | updated_at | incremental |  |
| item_family | medium | top-level parent | updated_at | updated_at | incremental |  |
| item_price | medium | top-level parent | updated_at | updated_at | incremental |  |
| order | medium | top-level parent | updated_at | updated_at | incremental |  |
| payment_source | medium | top-level parent | updated_at | updated_at | incremental |  |
| plan | medium | top-level parent | updated_at | updated_at | incremental |  |
| promotional_credit | medium | top-level parent | created_at | created_at | incremental |  |
| quote | medium | top-level parent | updated_at | updated_at | incremental |  |
| site_migration_detail | medium | top-level parent | migrated_at | migrated_at | incremental |  |
| subscription | medium | top-level parent | updated_at | updated_at | incremental |  |
| transaction | medium | top-level parent | updated_at | updated_at | incremental |  |
| unbilled_charge | medium | top-level parent | updated_at | updated_at | incremental |  |
| virtual_bank_account | medium | top-level parent | updated_at | updated_at | incremental |  |
| attached_item | medium | child | none | none | deferred_child |  |
| contact | medium | child | none | none | deferred_child |  |
| quote_line_group | medium | child | none | none | deferred_child |  |
| subscription_with_scheduled_changes | medium | child | none | none | deferred_child |  |

### Deferred streams

- **Child streams (4 streams):** `attached_item`, `contact`, `quote_line_group`, `subscription_with_scheduled_changes` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
