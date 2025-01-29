# Revolut Merchant
This is the Revolut Merchant source that ingests data from the Revolut Merchant API.

Revolut helps you spend, send, and save smarter https://www.revolut.com/

The Revolut Merchant account is a sub-account of your Revolut Business account. While a Business account is for managing your business finances, the Merchant account is dedicated to helping you accept online payments from your e-commerce customers.

This source uses the Merchant API and has the orders, customers and location endpoints. In order to use this API, you must first create a Revolut account. 
Log in to your Revolut Business account: Access the Revolut Business log in page and enter your credentials.
Navigate to Merchant API settings: Once logged in, access the Merchant API settings page by clicking your profile icon in the top left corner, then selecting APIs &gt; Merchant API. 
Here you can access your Production API keys (Public, Secret) specific to your Merchant account.
Get API keys: If you&#39;re visiting this page for the first time, you&#39;ll need to initiate the process by clicking the Get started button. To generate your Production API Secret key, click the Generate button.
You can find more about the API here https://developer.revolut.com/docs/merchant/merchant-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `secret_api_key` | `string` | Secret API Key. Secret API key to use for authenticating with the Revolut Merchant API. Find it in your Revolut Business account under APIs > Merchant API. |  |
| `start_date` | `string` | Start date.  |  |
| `environment` | `string` | environment. The base url of your environment. Either sandbox or production |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | No pagination | ✅ |  ❌  |
| locations | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-18 | [51894](https://github.com/airbytehq/airbyte/pull/51894) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51304](https://github.com/airbytehq/airbyte/pull/51304) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50679](https://github.com/airbytehq/airbyte/pull/50679) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50256](https://github.com/airbytehq/airbyte/pull/50256) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49704](https://github.com/airbytehq/airbyte/pull/49704) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49326](https://github.com/airbytehq/airbyte/pull/49326) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49052](https://github.com/airbytehq/airbyte/pull/49052) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-27 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
