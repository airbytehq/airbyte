import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Amazon Seller Partner Migration Guide

## Upgrading to 7.0.0

Amazon [deprecated](https://developer-docs.amazon.com/sp-api/docs/sp-api-deprecations) the Flat File Settlement Report (`GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`) on March 17, 2025 and [removes it on November 11, 2026](https://developer-docs.amazon.com/sp-api/changelog/update-removal-of-xml-settlement-report-and-flat-file-settlement-report-date-changed-to-november-11-2026). This version removes the `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` stream and adds its replacement, `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` (Flat File V2 Settlement Report).

The V2 report has a different schema. Instead of separate price and fee column pairs, each charge, fee or credit is a row with three general-purpose columns:

- `amount-type`: the type of charge or fee.
- `amount-description`: the specific charge or fee within that type.
- `amount`: the value. Amazon formats it in the marketplace's local currency format, for example `95,00` for EU marketplaces instead of `95.00`. The connector emits it as a string.

These columns from the old stream are not in the V2 report: `shipment-fee-type`, `shipment-fee-amount`, `order-fee-type`, `order-fee-amount`, `price-type`, `price-amount`, `item-related-fee-type`, `item-related-fee-amount`, `misc-fee-amount`, `other-fee-amount`, `other-fee-reason-description`, `promotion-type`, `promotion-amount`, `direct-payment-type`, `direct-payment-amount` and `other-amount`. The V2 report adds `posted-date-time`.

The V2 report writes timestamps as `2026-09-14 22:51:31 UTC`. The connector converts them to ISO 8601 (`2026-09-14T22:51:31+00:00`), the same format the old stream used. In the V2 stream, `posted-date` contains only the date, for example `2026-09-14`; the time is in `posted-date-time`.

The V2 report is available to Seller Central sellers only, and it requires the **Finance and Accounting** role. The old report also accepted the Inventory and Order Tracking or Amazon Fulfillment roles. If your app doesn't have the Finance and Accounting role, Amazon rejects requests for the V2 report: add the role to your app in Seller Central, then re-authenticate the source in Airbyte.

If you set Report Options for `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`, the connector removes them automatically when it upgrades. They never had an effect, because Amazon generates settlement reports on its own schedule.

### Who is affected

Connections that sync the `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` stream. Other streams are not affected.

### Steps to upgrade

1. Select **Connections** in the main navbar, then select the affected connection.
2. Select the **Schema** tab, then select **Refresh source schema**. `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` no longer appears.
3. Make sure your app has the **Finance and Accounting** role. If you add the role, re-authenticate the source.
4. Enable the `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` stream, then save the connection.
5. Update downstream SQL, dbt models and dashboards to read amounts from the `amount-type`, `amount-description` and `amount` columns, and parse `amount` according to the marketplace's number format.

The new stream writes to a new destination table, so you don't need to clear any stream. The existing `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` table is left as-is and stops receiving data. Keep it if you need settlement history: Amazon only lists settlement reports created in the last 90 days, so the first sync of the V2 stream starts at most 89 days back.

:::warning
Amazon generates both settlement reports for every settlement, with the same `settlement-id`. The settlements from the last 89 days will be in both tables after the first V2 sync. If you combine the two tables, deduplicate by `settlement-id`, for example by taking only settlements from the old table that aren't in the V2 table, or you will count those settlements twice.
:::

## Upgrading to 6.0.0

The primary key has been removed from the `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` and `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` streams.

These Amazon flat-file reports contain one row per order item, so the previous primary key (`amazon-order-id`) is not unique: when these streams were synced with `Incremental | Append + Deduped`, the destination collapsed all line items of a multi-item order into a single row, silently dropping data. No column or combination of columns in these reports has been proven to be reliably unique per row, so the streams now have no primary key.

After upgrading, refresh the source schema for your connection. Then:

**If either stream used `Incremental | Append + Deduped`**, your destination table is missing line items and must be reloaded:

:::danger
Clearing a stream deletes its data in the destination. Amazon only supplies order reports for orders less than two years old, and the connector only requests data from your **Replication Start Date** onward, so rows older than that cannot be re-synced. Take a snapshot or backup of the two destination tables before clearing if you need that history.
:::

1. Change the sync mode of `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` and `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` to `Incremental | Append` (or `Full Refresh | Overwrite`). `Incremental | Append + Deduped` is no longer offered for these streams.
2. Clear both streams and run a sync.

**If these streams used `Incremental | Append`, `Full Refresh | Append`, or `Full Refresh | Overwrite`**, no further action is required. Your existing rows are complete; do not clear the streams.

**Downstream impact.** After the reload, these tables contain one row per order *item*, not one row per order. Update SQL, dbt models, and dashboards that count rows as orders or that assume `amazon-order-id` is unique (for example, use `COUNT(DISTINCT "amazon-order-id")` for order counts, and group by `amazon-order-id` before summing item-level amounts). If you use a lookback window, deduplicate downstream on the full row or on `_airbyte_extracted_at`, since the destination no longer deduplicates for you.

## Upgrading to 5.0.0

Two deprecated FBA Subscribe and Save report types have been removed from the connector per Amazon SP-API deprecation:

- `GET_FBA_SNS_FORECAST_DATA` (Subscribe and Save Forecast Report)
- `GET_FBA_SNS_PERFORMANCE_DATA` (Subscribe and Save Performance Report)

These report types were deprecated by Amazon and will return empty responses starting July 25, 2025, and will be completely removed on December 11, 2025. See [Amazon's deprecation notice](https://developer-docs.amazon.com/sp-api/changelog/deprecation-of-two-fba-subscribe-and-save-report-types) for more details.

### Action Required

If you have these streams enabled in your connection:

1. **Refresh the source schema** to remove the deprecated streams from your catalog
2. **No data reset is required** - these streams are simply being removed from the available streams list

### Steps to Update

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
The deprecated streams will no longer appear in your available streams list.
```

3. Select **Save changes** at the bottom of the page.

```note
No data reset is required for this upgrade as the streams are being removed, not modified.
```

4. Select **Save connection**.

For more information on managing your Airbyte connections, see the [Airbyte documentation](/platform/operator-guides/clear).

## Upgrading to 4.0.0

Stream `GET_FBA_STORAGE_FEE_CHARGES_DATA` now has updated schema, which matches Amazon Seller Partner [docs](https://developer-docs.amazon.com/sp-api/docs/fba-inventory-reports-attributes#get_fba_storage_fee_charges_data).

Users will need to refresh the source schema and reset this stream after upgrading.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 3.0.0

Streams `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` and `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` now have updated schemas.

The following streams now have date-time formatted fields:

| Stream                                        | Affected fields                                                               | Format change                                                        |
| --------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | `estimated-arrival-date`                                                      | `string YYYY-MM-DDTHH:mm:ssZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ`    |
| `GET_LEDGER_DETAIL_VIEW_DATA`                 | `Date and Time`                                                               | `string YYYY-MM-DDTHH:mm:ssZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ`    |
| `GET_MERCHANTS_LISTINGS_FYP_REPORT`           | `Status Change Date`                                                          | `string MMM D[,] YYYY` -> `date-time YYYY-MM-DD`                     |
| `GET_STRANDED_INVENTORY_UI_DATA`              | `Date-to-take-auto-removal`                                                   | `string YYYY-MM-DDTHH:mm:ssZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ`    |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`     | `settlement-start-date`, `settlement-end-date`, `deposit-date`, `posted-date` | `string YYYY-MM-DDTHH:mm:ssZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ`    |
| `GET_MERCHANT_LISTINGS_ALL_DATA`              | `open-date`                                                                   | `string YYYY-MM-DD HH:mm:ss ZZZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ` |
| `GET_MERCHANT_LISTINGS_DATA`                  | `open-date`                                                                   | `string YYYY-MM-DD HH:mm:ss ZZZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ` |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA`         | `open-date`                                                                   | `string YYYY-MM-DD HH:mm:ss ZZZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ` |
| `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT`      | `open-date`                                                                   | `string YYYY-MM-DD HH:mm:ss ZZZ` -> `date-time YYYY-MM-DDTHH:mm:ssZ` |

Users will need to refresh the source schemas and reset these streams after upgrading.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

This change removes Brand Analytics and permanently removes deprecated FBA reports (from Airbyte Cloud).
Customers who have those streams must refresh their schema OR disable the following streams:

- `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT`
- `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT`
- `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT`
- `GET_BRAND_ANALYTICS_ALTERNATE_PURCHASE_REPORT`
- `GET_BRAND_ANALYTICS_ITEM_COMPARISON_REPORT`
- `GET_SALES_AND_TRAFFIC_REPORT`
- `GET_VENDOR_SALES_REPORT`
- `GET_VENDOR_INVENTORY_REPORT`

Customers, who have the following streams, will have to disable them:

- `GET_FBA_FULFILLMENT_INVENTORY_ADJUSTMENTS_DATA`
- `GET_FBA_FULFILLMENT_CURRENT_INVENTORY_DATA`
- `GET_FBA_FULFILLMENT_INVENTORY_RECEIPTS_DATA`
- `GET_FBA_FULFILLMENT_INVENTORY_SUMMARY_DATA`
- `GET_FBA_FULFILLMENT_MONTHLY_INVENTORY_DATA`

## Connector upgrade guide

<MigrationGuide />
