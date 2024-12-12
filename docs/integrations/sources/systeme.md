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
| 0.0.2 | 2024-12-11 | [49124](https://github.com/airbytehq/airbyte/pull/49124) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
