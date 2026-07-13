# Mercado Ads Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 updates the connector to match breaking changes in the Mercado Ads API across Brand Ads, Product Ads, and Display Ads. Stream schemas, endpoints, and response structures changed for most entity and metrics streams. The connector was also migrated to Connector Builder format 7.x.

This release adds one new stream:

- `display_creatives_metrics` — incremental metrics at the creative level for Display Ads

The following existing streams are unchanged and do not require migration steps:

- `brand_advertisers`
- `display_advertisers`
- `product_advertisers`

### Affected streams

Users with existing connections should refresh schemas and clear data for these streams before or immediately after upgrading to 1.0.0:

- `brand_campaigns`
- `brand_campaigns_metrics`
- `brand_items`
- `brand_keywords`
- `brand_keywords_metrics`
- `display_campaigns`
- `display_campaigns_metrics`
- `display_line_items`
- `display_line_items_metrics`
- `display_creatives`
- `product_campaigns`
- `product_campaigns_metrics`
- `product_items`
- `product_items_metrics`

## Migration Steps

To migrate an existing connection:

1. Select **Connections** in the main nav bar and open the connection using Mercado Ads.
2. Select the **Schema** tab and click **Refresh source schema** to pick up updated stream definitions.
3. Select the **Status** tab.
4. For each affected stream listed above, click the three dots on the right side of the stream and select **Clear Data**.
5. After clearing affected streams, click **Sync Now** to backfill data with the updated schemas.

For more information on clearing stream data in Airbyte, see [this page](/platform/operator-guides/clear).

If you are setting up a new connection, you can enable streams and sync normally on version 1.0.0 without following these steps.
