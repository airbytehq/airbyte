# Humanitix
Humanitix is a ticketing platform.
Using this connector we can extract data from streams such as events , orders and tickets.
Docs : https://humanitix.stoplight.io/docs/humanitix-public-api/e508a657c1467-humanitix-public-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | _id | DefaultPaginator | ✅ |  ❌  |
| orders | _id | DefaultPaginator | ✅ |  ❌  |
| tickets | _id | DefaultPaginator | ✅ |  ❌  |
| tags | _id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-06-14 | [61138](https://github.com/airbytehq/airbyte/pull/61138) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60671](https://github.com/airbytehq/airbyte/pull/60671) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59891](https://github.com/airbytehq/airbyte/pull/59891) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59290](https://github.com/airbytehq/airbyte/pull/59290) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58779](https://github.com/airbytehq/airbyte/pull/58779) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58181](https://github.com/airbytehq/airbyte/pull/58181) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57727](https://github.com/airbytehq/airbyte/pull/57727) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57079](https://github.com/airbytehq/airbyte/pull/57079) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56671](https://github.com/airbytehq/airbyte/pull/56671) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56071](https://github.com/airbytehq/airbyte/pull/56071) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55509](https://github.com/airbytehq/airbyte/pull/55509) | Update dependencies |
| 0.0.12 | 2025-03-01 | [54778](https://github.com/airbytehq/airbyte/pull/54778) | Update dependencies |
| 0.0.11 | 2025-02-22 | [53822](https://github.com/airbytehq/airbyte/pull/53822) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53307](https://github.com/airbytehq/airbyte/pull/53307) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52754](https://github.com/airbytehq/airbyte/pull/52754) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52293](https://github.com/airbytehq/airbyte/pull/52293) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51785](https://github.com/airbytehq/airbyte/pull/51785) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51210](https://github.com/airbytehq/airbyte/pull/51210) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50646](https://github.com/airbytehq/airbyte/pull/50646) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50074](https://github.com/airbytehq/airbyte/pull/50074) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49618](https://github.com/airbytehq/airbyte/pull/49618) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49261](https://github.com/airbytehq/airbyte/pull/49261) | Update dependencies |
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
