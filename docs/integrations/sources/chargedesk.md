# Chargedesk
This is the setup for the Chargedesk source that ingests data from the chargedesk API.

[ChargeDesk](https://chargedesk.com/) integrates directly with many of the most popular payment gateways including Stripe, WooCommerce, PayPal, Braintree Payments, Recurly, Authorize.Net, Zuora and Shopify. 

In order to use this source, you must first create an account. Once verified and logged in, head over to Setup -> API / Webhooks -> Issue New Key to generate your API key.

You can find more about the API here https://chargedesk.com/api-docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |
| `start_date` | `integer` | Start Date. Date from when the sync should start in epoch Unix timestamp |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| charges | charge_id | DefaultPaginator | ✅ |  ✅  |
| customers | customer_id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | subscription_id | DefaultPaginator | ✅ |  ✅  |
| products | product_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2024-12-14 | [49554](https://github.com/airbytehq/airbyte/pull/49554) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49309](https://github.com/airbytehq/airbyte/pull/49309) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49037](https://github.com/airbytehq/airbyte/pull/49037) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48205](https://github.com/airbytehq/airbyte/pull/48205) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47832](https://github.com/airbytehq/airbyte/pull/47832) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47560](https://github.com/airbytehq/airbyte/pull/47560) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
