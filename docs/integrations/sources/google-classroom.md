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
| 0.0.10 | 2025-02-08 | [53349](https://github.com/airbytehq/airbyte/pull/53349) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52818](https://github.com/airbytehq/airbyte/pull/52818) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52366](https://github.com/airbytehq/airbyte/pull/52366) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51669](https://github.com/airbytehq/airbyte/pull/51669) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51128](https://github.com/airbytehq/airbyte/pull/51128) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50545](https://github.com/airbytehq/airbyte/pull/50545) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50010](https://github.com/airbytehq/airbyte/pull/50010) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49540](https://github.com/airbytehq/airbyte/pull/49540) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49188](https://github.com/airbytehq/airbyte/pull/49188) | Update dependencies |
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
