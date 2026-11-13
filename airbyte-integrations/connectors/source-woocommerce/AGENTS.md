> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-woocommerce

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The WooCommerce REST API supports `modified_after` filtering on high-volume endpoints (orders, products, customers, etc.), which the connector already uses for incremental streams. The remaining FR parent streams are small config-style lookups (payment_gateways, product_attributes, shipping_methods, tax_classes, etc.) that do not support date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| coupons | medium | top-level parent | date_modified_gmt | date_modified_gmt | incremental |  |
| customers | medium | top-level parent | date_modified_gmt | date_modified_gmt | incremental |  |
| orders | medium | top-level parent | date_modified_gmt | date_modified_gmt | incremental |  |
| payment_gateways | small | top-level parent | none | none | deferred_no_api_support | Config-style; typically <10 items |
| product_attributes | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| product_categories | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| product_reviews | medium | top-level parent | date_created_gmt | date_created_gmt | incremental |  |
| product_shipping_classes | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| product_tags | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| products | medium | top-level parent | date_modified_gmt | date_modified_gmt | incremental |  |
| shipping_methods | small | top-level parent | none | none | deferred_no_api_support | Config-style; typically <10 items |
| shipping_zones | small | top-level parent | none | none | deferred_no_api_support | Config-style; typically <10 items |
| system_status_tools | small | top-level parent | none | none | deferred_no_api_support | Diagnostic endpoint |
| tax_classes | small | top-level parent | none | none | deferred_no_api_support | Config-style; typically <10 items |
| tax_rates | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| order_notes | medium | child | none | none | deferred_child |  |
| product_attribute_terms | medium | child | none | none | deferred_child |  |
| product_variations | medium | child | none | none | deferred_child |  |
| refunds | medium | child | none | none | deferred_child |  |
| shipping_zone_locations | medium | child | none | none | deferred_child |  |
| shipping_zone_methods | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (10 streams):** `payment_gateways`, `product_attributes`, `product_categories`, `product_shipping_classes`, `product_tags`, `shipping_methods`, `shipping_zones`, `system_status_tools`, `tax_classes`, `tax_rates` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (6 streams):** `order_notes`, `product_attribute_terms`, `product_variations`, `refunds`, `shipping_zone_locations`, `shipping_zone_methods` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
