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
| 0.0.1 | 2024-10-30 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
