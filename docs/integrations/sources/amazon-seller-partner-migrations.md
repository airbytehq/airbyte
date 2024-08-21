# Amazon Seller Partner Migration Guide

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

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

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

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

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
