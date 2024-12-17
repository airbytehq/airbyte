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
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
