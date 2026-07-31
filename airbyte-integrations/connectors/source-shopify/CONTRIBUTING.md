# Contributing to source-shopify

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Shopify REST and GraphQL Admin APIs support `updated_at_min` filtering on most resource endpoints. The connector is a Python CDK connector with comprehensive incremental patterns: `IncrementalShopifyStream` (REST with `updated_at_min`), `IncrementalShopifyGraphQlBulkStream` (GraphQL Bulk Operations), `IncrementalShopifySubstream`, `IncrementalShopifyNestedStream`, and `IncrementalShopifyStreamWithDeletedEvents` (tracks both updates and deletions via Events API).

**Connector type:** Python CDK

**Analysis status:** Complete stream-by-stream analysis performed. Nearly all streams (40+) already use incremental sync with appropriate cursor fields. Only 3 streams are full-refresh, all correctly so.

### Already Incremental Streams (Partial List)

The connector has 40+ incremental streams across REST, GraphQL Bulk, substream, and nested patterns. Key examples:

| Stream | Cursor Field | Pattern | Notes |
|--------|-------------|---------|-------|
| Orders | updated_at | IncrementalShopifyStreamWithDeletedEvents | Tracks updates + deletions |
| Products | updated_at | IncrementalShopifyGraphQlBulkStream | GraphQL Bulk Operations |
| Customers | updated_at | IncrementalShopifyStream | REST with `updated_at_min` |
| Articles | updated_at | IncrementalShopifyStreamWithDeletedEvents | Tracks updates + deletions |
| Collections | updated_at | IncrementalShopifyGraphQlBulkStream | GraphQL Bulk |
| InventoryLevels | updated_at | IncrementalShopifyGraphQlBulkStream | GraphQL Bulk |
| Fulfillments | updated_at | IncrementalShopifyNestedStream | Nested under Orders |
| Transactions | created_at | IncrementalShopifySubstream | Child of Orders |
| All Metafield streams | updated_at | Various | 10+ metafield substreams |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| Locations | No date-based filtering | Shopify REST API `GET /admin/api/{version}/locations.json` does not support `updated_at_min` parameter; locations rarely change |
| Shop | Single record | Returns one record per Shopify store; no incremental benefit |
| Countries | Small reference dataset | `HttpSubStream` + `FullRefreshShopifyGraphQlBulkStream`; shipping country configuration rarely changes |
