# Systeme
Systeme is an all in one marketing platform.
Using this connector we can extarct records from communities , contacts , tags , contact fields and course resources streams.
Docs : https://developer.systeme.io/reference/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| communities | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| contact_fields |  | DefaultPaginator | ✅ |  ❌  |
| course_resources | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [53046](https://github.com/airbytehq/airbyte/pull/53046) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52450](https://github.com/airbytehq/airbyte/pull/52450) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51996](https://github.com/airbytehq/airbyte/pull/51996) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51427](https://github.com/airbytehq/airbyte/pull/51427) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50817](https://github.com/airbytehq/airbyte/pull/50817) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50307](https://github.com/airbytehq/airbyte/pull/50307) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49763](https://github.com/airbytehq/airbyte/pull/49763) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49428](https://github.com/airbytehq/airbyte/pull/49428) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49124](https://github.com/airbytehq/airbyte/pull/49124) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
