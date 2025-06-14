# Cloudbeds
This is Cloudbeds source that ingests data from the Cloudbeds API.

Cloudbeds is an unified hospitality platform https://cloudbeds.com

In order to use this source, you must first create a cloudbeds account. Once logged in, navigate to the API credentials page for your property by clicking Account > Apps & Marketplace in the upper right corner.  Use the menu on the top to navigate to the API Credentials Page. Click the New Credentials button, fill in the details and click on Create. This will create an application, then click on the API Key and provide all the required scopes as needed. 

You can learn more about the API here https://hotels.cloudbeds.com/api/v1.2/docs/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| guests | guestID | DefaultPaginator | ✅ |  ❌  |
| hotels |  | DefaultPaginator | ✅ |  ❌  |
| rooms | propertyID | DefaultPaginator | ✅ |  ❌  |
| reservations | reservationID | DefaultPaginator | ✅ |  ❌  |
| transactions | transactionID | DefaultPaginator | ✅ |  ❌  |
| packages | itemID | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.24 | 2025-06-14 | [61199](https://github.com/airbytehq/airbyte/pull/61199) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60410](https://github.com/airbytehq/airbyte/pull/60410) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60033](https://github.com/airbytehq/airbyte/pull/60033) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59447](https://github.com/airbytehq/airbyte/pull/59447) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58901](https://github.com/airbytehq/airbyte/pull/58901) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58324](https://github.com/airbytehq/airbyte/pull/58324) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57795](https://github.com/airbytehq/airbyte/pull/57795) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57253](https://github.com/airbytehq/airbyte/pull/57253) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56541](https://github.com/airbytehq/airbyte/pull/56541) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55964](https://github.com/airbytehq/airbyte/pull/55964) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55278](https://github.com/airbytehq/airbyte/pull/55278) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54981](https://github.com/airbytehq/airbyte/pull/54981) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54443](https://github.com/airbytehq/airbyte/pull/54443) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53706](https://github.com/airbytehq/airbyte/pull/53706) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53350](https://github.com/airbytehq/airbyte/pull/53350) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52804](https://github.com/airbytehq/airbyte/pull/52804) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52335](https://github.com/airbytehq/airbyte/pull/52335) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51660](https://github.com/airbytehq/airbyte/pull/51660) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51074](https://github.com/airbytehq/airbyte/pull/51074) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50555](https://github.com/airbytehq/airbyte/pull/50555) | Update dependencies |
| 0.0.4 | 2024-12-21 | [49992](https://github.com/airbytehq/airbyte/pull/49992) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49487](https://github.com/airbytehq/airbyte/pull/49487) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48925](https://github.com/airbytehq/airbyte/pull/48925) | Update dependencies |
| 0.0.1 | 2024-10-31 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
