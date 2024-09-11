# Buildkite
Website: https://buildkite.com/
Auth page: https://buildkite.com/user/api-access-tokens
API Docs: https://buildkite.com/docs/apis/rest-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organizations | id | DefaultPaginator | ✅ |  ✅  |
| analytics_organizations_suites | id | DefaultPaginator | ✅ |  ❌  |
| organizations_pipelines | id | DefaultPaginator | ✅ |  ✅  |
| access-token | uuid | DefaultPaginator | ✅ |  ❌  |
| builds | id | DefaultPaginator | ✅ |  ✅  |
| organizations_clusters | id | DefaultPaginator | ✅ |  ✅  |
| organizations_builds | id | DefaultPaginator | ✅ |  ✅  |
| organizations_pipelines_builds | id | DefaultPaginator | ✅ |  ✅  |
| organizations_clusters_queues | id | DefaultPaginator | ✅ |  ✅  |
| organizations_clusters_tokens | id | DefaultPaginator | ✅ |  ✅  |
| organizations_emojis |  | DefaultPaginator | ✅ |  ❌  |
| user | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-11 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>