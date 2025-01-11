# Shipstation
This page contains the setup guide and reference information for Shipstation source connector.

Documentation reference:
Visit https://www.shipstation.com/docs/api/ for API documentation

Authentication setup

To get your API key and secret in ShipStation:

↳ Go to Account Settings.

↳ Select Account from the side navigation, then choose API Settings.

↳ Click &quot;Generate New API Keys&quot; if no key and secret are listed yet.

** IMPORTANT **
↳If you&#39;ve already generated your API keys, the existing API keys will be displayed here and the button will read Regenerate API Keys.

If you already have API keys, do NOT generate new ones. Instead, copy your existing key and secret.

Copy your key and secret and paste them into the respective fields.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | API Key.  |  |
| `password` | `string` | API Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| carriers | shippingProviderId | No pagination | ✅ |  ❌  |
| customers | customerId | DefaultPaginator | ✅ |  ❌  |
| fulfillments | fulfillmentId | DefaultPaginator | ✅ |  ❌  |
| orders | orderId | DefaultPaginator | ✅ |  ❌  |
| products | productId | DefaultPaginator | ✅ |  ❌  |
| shipments | shipmentId | DefaultPaginator | ✅ |  ❌  |
| marketplaces | name.marketplaceId | No pagination | ✅ |  ❌  |
| stores | storeId | No pagination | ✅ |  ❌  |
| users | userId | No pagination | ✅ |  ❌  |
| warehouses | warehouseId | No pagination | ✅ |  ❌  |
| webhooks | WebHookID | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-01-11 | [51328](https://github.com/airbytehq/airbyte/pull/51328) | Update dependencies |
| 0.0.2 | 2024-12-28 | [50726](https://github.com/airbytehq/airbyte/pull/50726) | Update dependencies |
| 0.0.1 | 2024-12-21 | | Initial release by [@JohnnyRafael](https://github.com/JohnnyRafael) via Connector Builder |

</details>
