# Navan

The Navan connector supports travel booking data such as hotels and flights. 

## Prerequisites

* Client ID and Client Secret - Credentials for accessing the Navan API that can be created by administrators. 
  * Learn how to create these API credentials by following [documentation provided by Navan](https://app.navan.com/app/helpcenter/articles/travel/admin/other-integrations/booking-data-integration). Note that API credential details are only accessible once.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bookings | uuid | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51174](https://github.com/airbytehq/airbyte/pull/51174) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50642](https://github.com/airbytehq/airbyte/pull/50642) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50106](https://github.com/airbytehq/airbyte/pull/50106) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49599](https://github.com/airbytehq/airbyte/pull/49599) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49217](https://github.com/airbytehq/airbyte/pull/49217) | Update dependencies |
| 0.0.1 | 2024-11-26 | | Initial release by [@matteogp](https://github.com/matteogp) via Connector Builder |

</details>
