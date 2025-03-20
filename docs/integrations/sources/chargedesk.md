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
| 0.0.18 | 2025-03-08 | [55397](https://github.com/airbytehq/airbyte/pull/55397) | Update dependencies |
| 0.0.17 | 2025-03-01 | [54875](https://github.com/airbytehq/airbyte/pull/54875) | Update dependencies |
| 0.0.16 | 2025-02-22 | [54210](https://github.com/airbytehq/airbyte/pull/54210) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53893](https://github.com/airbytehq/airbyte/pull/53893) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53420](https://github.com/airbytehq/airbyte/pull/53420) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52884](https://github.com/airbytehq/airbyte/pull/52884) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52173](https://github.com/airbytehq/airbyte/pull/52173) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51731](https://github.com/airbytehq/airbyte/pull/51731) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51278](https://github.com/airbytehq/airbyte/pull/51278) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50448](https://github.com/airbytehq/airbyte/pull/50448) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50170](https://github.com/airbytehq/airbyte/pull/50170) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49554](https://github.com/airbytehq/airbyte/pull/49554) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49309](https://github.com/airbytehq/airbyte/pull/49309) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49037](https://github.com/airbytehq/airbyte/pull/49037) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48205](https://github.com/airbytehq/airbyte/pull/48205) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47832](https://github.com/airbytehq/airbyte/pull/47832) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47560](https://github.com/airbytehq/airbyte/pull/47560) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
