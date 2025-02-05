# Cin7 Inventory API
This is the Cin7 source that ingests data from the Cin7 API.

Cin7 (Connector Inventory Performance), If you’re a business that wants to grow, you need an inventory solution you can count on - both now and in the future. With Cin7 you get a real-time picture of your products across systems, channels, marketplaces and regions, plus NEW ForesightAI advanced inventory forecasting that empowers you to see around corners and stay three steps ahead of demand! https://www.cin7.com/

To use this source, you must first create an account. Once logged in, head to Integrations -&gt; API -&gt; Cin7 Core API.
Create an application and note down the Account Id and the API key, you will need to enter these in the input fields. You can find more information about the [API Documentation](https://dearinventory.docs.apiary.io/#reference)


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `accountid` | `string` | AccountID. The ID associated with your account. |  |
| `api_key` | `string` | API Key. The API key associated with your account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bank_accounts | AccountID | DefaultPaginator | ✅ |  ❌  |
| attribute_sets | ID | DefaultPaginator | ✅ |  ❌  |
| accounts | Code | DefaultPaginator | ✅ |  ❌  |
| brands | ID | DefaultPaginator | ✅ |  ❌  |
| carriers | CarrierID | DefaultPaginator | ✅ |  ❌  |
| customers | ID | DefaultPaginator | ✅ |  ❌  |
| deals | ID | No pagination | ✅ |  ❌  |
| locations |  | DefaultPaginator | ✅ |  ❌  |
| products | ID | DefaultPaginator | ✅ |  ❌  |
| purchases | ID | DefaultPaginator | ✅ |  ❌  |
| suppliers | ID | DefaultPaginator | ✅ |  ❌  |
| product_categories | ID | DefaultPaginator | ✅ |  ❌  |
| sale_lists | ID | DefaultPaginator | ✅ |  ❌  |
| product_families | ID | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [52880](https://github.com/airbytehq/airbyte/pull/52880) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52177](https://github.com/airbytehq/airbyte/pull/52177) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51718](https://github.com/airbytehq/airbyte/pull/51718) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51227](https://github.com/airbytehq/airbyte/pull/51227) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50466](https://github.com/airbytehq/airbyte/pull/50466) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50191](https://github.com/airbytehq/airbyte/pull/50191) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49576](https://github.com/airbytehq/airbyte/pull/49576) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49284](https://github.com/airbytehq/airbyte/pull/49284) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48950](https://github.com/airbytehq/airbyte/pull/48950) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
