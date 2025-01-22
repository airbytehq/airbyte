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
| 0.0.9 | 2025-01-18 | [51797](https://github.com/airbytehq/airbyte/pull/51797) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51207](https://github.com/airbytehq/airbyte/pull/51207) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50142](https://github.com/airbytehq/airbyte/pull/50142) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49623](https://github.com/airbytehq/airbyte/pull/49623) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49263](https://github.com/airbytehq/airbyte/pull/49263) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48276](https://github.com/airbytehq/airbyte/pull/48276) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47907](https://github.com/airbytehq/airbyte/pull/47907) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47609](https://github.com/airbytehq/airbyte/pull/47609) | Update dependencies |
| 0.0.1 | 2024-09-23 | | Initial release by [@FilipeJesus](https://github.com/FilipeJesus) via Connector Builder |

</details>
