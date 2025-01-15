# GitBook
GitBook connector  enables seamless data integration from GitBook into your data pipelines. It efficiently extracts content, such as documentation and pages, allowing teams to sync and analyze information across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Personal access token for authenticating with the GitBook API. You can view and manage your access tokens in the Developer settings of your GitBook user account. |  |
| `space_id` | `string` | Space Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users |  | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| insights | timestamp | DefaultPaginator | ✅ |  ❌  |
| content | id | DefaultPaginator | ✅ |  ❌  |
| org_members | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-01-11 | [51061](https://github.com/airbytehq/airbyte/pull/51061) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50563](https://github.com/airbytehq/airbyte/pull/50563) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50002](https://github.com/airbytehq/airbyte/pull/50002) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49517](https://github.com/airbytehq/airbyte/pull/49517) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49166](https://github.com/airbytehq/airbyte/pull/49166) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48910](https://github.com/airbytehq/airbyte/pull/48910) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
