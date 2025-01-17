# Retail Express by Maropost
Retail Express by Maropost is an Australian retail point-of-sale, inventory management, fulfilment and multichannel ecommerce platform.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| countries | id | DefaultPaginator | ✅ |  ✅  |
| credit_notes | id | DefaultPaginator | ✅ |  ✅  |
| credit_note_items | id | DefaultPaginator | ✅ |  ✅  |
| currencies | id | DefaultPaginator | ✅ |  ✅  |
| customer_logs | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| customer_delivery_addresses | id | DefaultPaginator | ✅ |  ✅  |
| customer_types | id | DefaultPaginator | ✅ |  ✅  |
| freight_types | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| order_items | id | DefaultPaginator | ✅ |  ❌  |
| order_fulfilments | id | DefaultPaginator | ✅ |  ✅  |
| order_payments | id | DefaultPaginator | ✅ |  ✅  |
| outlets | id | DefaultPaginator | ✅ |  ❌  |
| product_attributes | id | DefaultPaginator | ✅ |  ❌  |
| product_attribute_values | id.attribute_id | DefaultPaginator | ✅ |  ❌  |
| product_replenishment_methods | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| product_types | id | DefaultPaginator | ✅ |  ❌  |
| purchase_orders | id | DefaultPaginator | ✅ |  ✅  |
| purchase_order_items | po_item_id | DefaultPaginator | ✅ |  ✅  |
| transfers | id | DefaultPaginator | ✅ |  ✅  |
| transfer_items | id | DefaultPaginator | ✅ |  ✅  |
| receipt_variance_reasons | id | DefaultPaginator | ✅ |  ✅  |
| shipment_types | id | DefaultPaginator | ✅ |  ❌  |
| shipping_ports | id | DefaultPaginator | ✅ |  ❌  |
| shipping_status | id | DefaultPaginator | ✅ |  ❌  |
| stock_receipts | id | DefaultPaginator | ✅ |  ✅  |
| supplier_invoices | id | DefaultPaginator | ✅ |  ✅  |
| supplier_return_item_source | id | DefaultPaginator | ✅ |  ❌  |
| supplier_return_item_status | id | DefaultPaginator | ✅ |  ❌  |
| supplier_return_reasons | id | DefaultPaginator | ✅ |  ✅  |
| supplier_return_status | id | DefaultPaginator | ✅ |  ❌  |
| supplier_returns | id | DefaultPaginator | ✅ |  ✅  |
| suppliers | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| vouchers | id | DefaultPaginator | ✅ |  ❌  |
| voucher_types | id | DefaultPaginator | ✅ |  ❌  |
| inventory | product_id.outlet_id | DefaultPaginator | ✅ |  ✅  |
| inventory_movement_logs | id | DefaultPaginator | ✅ |  ✅  |
| customer_survey_segments | id | DefaultPaginator | ✅ |  ❌  |
| loyalty_adjustment_reasons | id | DefaultPaginator | ✅ |  ❌  |
| max_discount_rules | id | DefaultPaginator | ✅ |  ✅  |
| price_groups_fixed | id | DefaultPaginator | ✅ |  ❌  |
| price_groups_standard | id | DefaultPaginator | ✅ |  ❌  |
| product_barcodes | id | DefaultPaginator | ✅ |  ✅  |
| product_prices | product_id.outlet_id | DefaultPaginator | ✅ |  ❌  |
| return_reasons | id | DefaultPaginator | ✅ |  ✅  |
| stock_adjustment_reasons | id | DefaultPaginator | ✅ |  ✅  |
| transfer_status | id | DefaultPaginator | ✅ |  ❌  |
| transfer_types | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-01-17 | | Initial release by [@GamesmenJordan](https://github.com/GamesmenJordan) via Connector Builder |

</details>
