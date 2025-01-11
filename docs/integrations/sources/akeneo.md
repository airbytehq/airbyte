# Akeneo
The Akeneo Airbyte connector enables seamless data synchronization between Akeneo PIM (Product Information Management) and other platforms. It allows you to easily extract, transform, and load product information from Akeneo to a desired data destination, facilitating efficient management and integration of product catalogs across systems. This connector supports bidirectional data flows, helping businesses maintain accurate and up-to-date product information for various sales channels.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `host` | `string` | Host.  |  |
| `api_username` | `string` | API Username.  |  |
| `password` | `string` | password.  |  |
| `client_id` | `string` | Client ID.  |  |
| `secret` | `string` | Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products | uuid | DefaultPaginator | ✅ |  ❌  |
| categories  | code | DefaultPaginator | ✅ |  ❌  |
| families | code | DefaultPaginator | ✅ |  ❌  |
| family_variants | code | DefaultPaginator | ✅ |  ❌  |
| attributes | code | DefaultPaginator | ✅ |  ❌  |
| attribute_groups | code | DefaultPaginator | ✅ |  ❌  |
| association_types | code | DefaultPaginator | ✅ |  ❌  |
| channels | code | DefaultPaginator | ✅ |  ❌  |
| locales |  | DefaultPaginator | ✅ |  ❌  |
| currencies | code | DefaultPaginator | ✅ |  ❌  |
| measure_families | code | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51285](https://github.com/airbytehq/airbyte/pull/51285) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50454](https://github.com/airbytehq/airbyte/pull/50454) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50160](https://github.com/airbytehq/airbyte/pull/50160) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49558](https://github.com/airbytehq/airbyte/pull/49558) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49011](https://github.com/airbytehq/airbyte/pull/49011) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
