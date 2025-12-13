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
| 0.0.45 | 2025-12-09 | [70660](https://github.com/airbytehq/airbyte/pull/70660) | Update dependencies |
| 0.0.44 | 2025-11-25 | [69905](https://github.com/airbytehq/airbyte/pull/69905) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69601](https://github.com/airbytehq/airbyte/pull/69601) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68864](https://github.com/airbytehq/airbyte/pull/68864) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68486](https://github.com/airbytehq/airbyte/pull/68486) | Update dependencies |
| 0.0.40 | 2025-10-14 | [68070](https://github.com/airbytehq/airbyte/pull/68070) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67188](https://github.com/airbytehq/airbyte/pull/67188) | Update dependencies |
| 0.0.38 | 2025-09-30 | [65854](https://github.com/airbytehq/airbyte/pull/65854) | Update dependencies |
| 0.0.37 | 2025-08-23 | [65235](https://github.com/airbytehq/airbyte/pull/65235) | Update dependencies |
| 0.0.36 | 2025-08-09 | [64681](https://github.com/airbytehq/airbyte/pull/64681) | Update dependencies |
| 0.0.35 | 2025-08-02 | [64325](https://github.com/airbytehq/airbyte/pull/64325) | Update dependencies |
| 0.0.34 | 2025-07-26 | [64027](https://github.com/airbytehq/airbyte/pull/64027) | Update dependencies |
| 0.0.33 | 2025-07-19 | [63551](https://github.com/airbytehq/airbyte/pull/63551) | Update dependencies |
| 0.0.32 | 2025-07-12 | [62955](https://github.com/airbytehq/airbyte/pull/62955) | Update dependencies |
| 0.0.31 | 2025-07-05 | [62762](https://github.com/airbytehq/airbyte/pull/62762) | Update dependencies |
| 0.0.30 | 2025-06-28 | [62309](https://github.com/airbytehq/airbyte/pull/62309) | Update dependencies |
| 0.0.29 | 2025-06-21 | [61942](https://github.com/airbytehq/airbyte/pull/61942) | Update dependencies |
| 0.0.28 | 2025-06-14 | [61170](https://github.com/airbytehq/airbyte/pull/61170) | Update dependencies |
| 0.0.27 | 2025-05-24 | [60365](https://github.com/airbytehq/airbyte/pull/60365) | Update dependencies |
| 0.0.26 | 2025-05-10 | [59989](https://github.com/airbytehq/airbyte/pull/59989) | Update dependencies |
| 0.0.25 | 2025-05-03 | [59317](https://github.com/airbytehq/airbyte/pull/59317) | Update dependencies |
| 0.0.24 | 2025-04-26 | [58716](https://github.com/airbytehq/airbyte/pull/58716) | Update dependencies |
| 0.0.23 | 2025-04-19 | [58284](https://github.com/airbytehq/airbyte/pull/58284) | Update dependencies |
| 0.0.22 | 2025-04-12 | [57600](https://github.com/airbytehq/airbyte/pull/57600) | Update dependencies |
| 0.0.21 | 2025-04-05 | [57160](https://github.com/airbytehq/airbyte/pull/57160) | Update dependencies |
| 0.0.20 | 2025-03-29 | [56566](https://github.com/airbytehq/airbyte/pull/56566) | Update dependencies |
| 0.0.19 | 2025-03-22 | [56158](https://github.com/airbytehq/airbyte/pull/56158) | Update dependencies |
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
