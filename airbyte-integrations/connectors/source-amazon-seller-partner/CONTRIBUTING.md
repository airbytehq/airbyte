# Contributing to source-amazon-seller-partner

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Amazon Seller Partner API uses an asynchronous report generation model. Most streams in the connector correspond to report types that are generated on-demand via `createReport` / `getReport`. The connector already uses `DatetimeBasedCursor` for 43 report streams. The remaining 8 FR parent streams are brand analytics and vendor reports that use different date range patterns not directly compatible with simple `updated_at` cursor filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| get_afn_inventory_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_afn_inventory_data_by_country | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_amazon_fulfilled_shipments_data_general | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_brand_analytics_alternate_purchase_report | medium | top-level parent | none | none | deferred_no_api_support | Brand analytics report; weekly/monthly aggregation |
| get_brand_analytics_item_comparison_report | medium | top-level parent | none | none | deferred_no_api_support | Brand analytics report; weekly/monthly aggregation |
| get_brand_analytics_market_basket_report | medium | top-level parent | none | none | deferred_no_api_support | Brand analytics report; weekly/monthly aggregation |
| get_brand_analytics_repeat_purchase_report | medium | top-level parent | none | none | deferred_no_api_support | Brand analytics report; weekly/monthly aggregation |
| get_brand_analytics_search_terms_report | medium | top-level parent | none | none | deferred_no_api_support | Brand analytics report; weekly/monthly aggregation |
| get_fba_estimated_fba_fees_txt_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_fulfillment_customer_returns_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_fulfillment_customer_shipment_promotion_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_fulfillment_customer_shipment_replacement_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_fulfillment_removal_order_detail_data | medium | top-level parent | last-updated-date | last-updated-date | incremental |  |
| get_fba_fulfillment_removal_shipment_detail_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_inventory_planning_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_myi_unsuppressed_inventory_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_reimbursements_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_fba_storage_fee_charges_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_flat_file_actionable_order_data_shipping | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_flat_file_all_orders_data_by_last_update_general | medium | top-level parent | last-updated-date | last-updated-date | incremental |  |
| get_flat_file_all_orders_data_by_order_date_general | medium | top-level parent | last-updated-date | last-updated-date | incremental |  |
| get_flat_file_archived_orders_data_by_order_date | medium | top-level parent | last-updated-date | last-updated-date | incremental |  |
| get_flat_file_open_listings_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_flat_file_returns_data_by_return_date | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_ledger_detail_view_data | medium | top-level parent | Date | Date | incremental |  |
| get_ledger_summary_view_data | medium | top-level parent | Date | Date | incremental |  |
| get_merchant_cancelled_listings_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_merchant_listings_all_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_merchant_listings_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_merchant_listings_data_back_compat | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_merchant_listings_inactive_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_merchants_listings_fyp_report | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_order_report_data_shipping | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_restock_inventory_recommendations_report | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_sales_and_traffic_report | medium | top-level parent | queryEndDate | queryEndDate | incremental |  |
| get_sales_and_traffic_report_by_date | medium | top-level parent | queryEndDate | queryEndDate | incremental |  |
| get_sales_and_traffic_report_by_month | medium | top-level parent | queryEndDate | queryEndDate | incremental |  |
| get_seller_feedback_data | medium | top-level parent | date | date | incremental |  |
| get_stranded_inventory_ui_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| get_vendor_forecasting_fresh_report | medium | top-level parent | none | none | deferred_no_api_support | Vendor forecast report; uses report date range, not cursor |
| get_vendor_forecasting_retail_report | medium | top-level parent | none | none | deferred_no_api_support | Vendor forecast report; uses report date range, not cursor |
| get_vendor_inventory_report | medium | top-level parent | none | none | deferred_no_api_support | Vendor inventory snapshot; no cursor support |
| get_vendor_sales_report | medium | top-level parent | endDate | endDate | incremental |  |
| get_xml_all_orders_data_by_order_date_general | medium | top-level parent | LastUpdatedDate | LastUpdatedDate | incremental |  |
| get_xml_browse_tree_data | medium | top-level parent | dataEndTime | dataEndTime | incremental |  |
| list_financial_event_groups | medium | top-level parent | FinancialEventGroupStart | FinancialEventGroupStart | incremental |  |
| list_financial_events | medium | top-level parent | PostedBefore | PostedBefore | incremental |  |
| orders | medium | top-level parent | LastUpdateDate | LastUpdateDate | incremental |  |
| vendor_direct_fulfillment_shipping | medium | top-level parent | createdBefore | createdBefore | incremental |  |
| vendor_orders | medium | top-level parent | changedBefore | changedBefore | incremental |  |
| vendor_orders_status | medium | top-level parent | createdBefore | createdBefore | incremental |  |
| get_v2_settlement_report_data_flat_file | medium | child | dataEndTime | dataEndTime | incremental |  |
| order_items | medium | child of orders | LastUpdateDate | LastUpdateDate | incremental |  |

### Deferred streams

- **No API date filter (8 streams):** `get_brand_analytics_alternate_purchase_report`, `get_brand_analytics_item_comparison_report`, `get_brand_analytics_market_basket_report`, `get_brand_analytics_repeat_purchase_report`, `get_brand_analytics_search_terms_report`, `get_vendor_forecasting_fresh_report`, `get_vendor_forecasting_retail_report`, `get_vendor_inventory_report` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
