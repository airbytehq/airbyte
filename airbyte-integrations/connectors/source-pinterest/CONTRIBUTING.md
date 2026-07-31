# Contributing to source-pinterest

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction and backoff strategy)

**Analysis status:** Complete. 32 streams analyzed. 20 use incremental sync (analytics reports with date cursors, management streams with `updated_time`). 12 are full-refresh.

### Incremental Streams (20)

| Category | Streams | Cursor Field | Notes |
|----------|---------|-------------|-------|
| Management | campaigns, ad_groups, ads | `updated_time` | Pinterest management API with cursor |
| Analytics | user/ad_account/campaign/ad_group/ad_analytics | `DATE` | Pinterest Analytics API with date range |
| Reports (11) | advertiser/ad_group/campaign/pin_promotion/product_group/product_item/campaign_targeting/advertiser_targeting/ad_group_targeting/pin_promotion_targeting/product_group_targeting/keyword reports | `DATE` | Pinterest Async Reporting API |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| boards | No `updated_time` filter on list endpoint | Pinterest Boards API returns all boards; no date filter |
| board_sections | Substream of boards; no date filter | Per-board endpoint |
| board_pins | Substream of boards; no date filter | Per-board pins endpoint |
| board_section_pins | Substream of board_sections; no date filter | Per-section endpoint |
| catalogs | No date filter | Pinterest Catalogs API returns all catalogs |
| catalogs_feeds | Substream of catalogs; no date filter | Per-catalog feeds |
| catalogs_product_groups | No date filter | Pinterest Catalogs Product Groups API |
| ad_accounts | Small dataset; no date filter | Returns all ad accounts for user |
| audiences | No date filter | Pinterest Audiences API has no `updated_since` |
| keywords | Substream of ad_groups; no date filter | Per-ad-group keywords |
| conversion_tags | No date filter | Pinterest Conversion Tags API |
| customer_lists | No date filter | Pinterest Customer Lists API |
