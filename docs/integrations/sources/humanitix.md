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
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
