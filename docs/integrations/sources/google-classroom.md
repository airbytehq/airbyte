# Google Classroom
Google Classroom connector enables seamless data integration between Google Classroom and various destinations. This connector facilitates the synchronization of course information, rosters, assignments empowering educators to automate reporting and streamline classroom data management efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| courses | id | DefaultPaginator | ✅ |  ❌  |
| teachers | userId | DefaultPaginator | ✅ |  ❌  |
| students | userId | DefaultPaginator | ✅ |  ❌  |
| announcements | id | DefaultPaginator | ✅ |  ❌  |
| coursework | id | DefaultPaginator | ✅ |  ❌  |
| studentsubmissions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
