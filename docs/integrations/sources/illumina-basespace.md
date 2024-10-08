# Illumina Basespace
Connector for the Basespace v1 API. This can be used to extract data on projects, runs, samples and app sessions.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. BaseSpace access token. Instructions for obtaining your access token can be found in the BaseSpace Developer Documentation. |  |
| `domain` | `string` | Domain. Domain name of the BaseSpace instance (e.g., euw2.sh.basespace.illumina.com) |  |
| `user` | `string` | User. Providing a user ID restricts the returned data to what that user can access. If you use the default (&#39;current&#39;), all data accessible to the user associated with the API key will be shown. | current |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | Id | DefaultPaginator | ✅ |  ❌  |
| runs | Id | DefaultPaginator | ✅ |  ❌  |
| samples | Id | DefaultPaginator | ✅ |  ❌  |
| sample_files | Id | DefaultPaginator | ✅ |  ❌  |
| run_files | Id | DefaultPaginator | ✅ |  ❌  |
| appsessions | Id | DefaultPaginator | ✅ |  ❌  |
| appresults | Id | DefaultPaginator | ✅ |  ❌  |
| appresults_files | Id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-23 | | Initial release by [@FilipeJesus](https://github.com/FilipeJesus) via Connector Builder |

</details>