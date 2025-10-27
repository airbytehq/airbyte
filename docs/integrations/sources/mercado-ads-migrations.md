# Mercado Ads Migration Guide

## Upgrading to 1.0.0

This release introduces changes to all streams corresponding to Brand Ads and Product Ads endpoints (those with the prefix `brand_` and `product_`). This is due to changes in the Mercado Ads API that changed the way data is retrieved and returned.

### Affected streams

- `brand_campaigns`
- `brand_campaigns_metrics`
- `brand_items`
- `brand_keywords`
- `brand_keywords_metrics`
- `product_campaigns`
- `product_campaigns_metrics`
- `product_items`
- `product_items_metrics`

## Migration Steps

To clear your data for the `brand_` and `product_` streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the affected stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**.
