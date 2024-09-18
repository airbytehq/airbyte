# Split-io
Website: https://app.split.io/
API Docs: https://docs.split.io/reference/introduction
Authentication docs: https://docs.split.io/reference/authentication
API Keys: vlru5ud5abuegn2nfdcfbcnjb63gdafashr3

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| changeRequests | id | DefaultPaginator | ✅ |  ❌  |
| workspaces | id | DefaultPaginator | ✅ |  ❌  |
| flagSets | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| segments | name | DefaultPaginator | ✅ |  ✅  |
| segments_keys | uid | DefaultPaginator | ✅ |  ❌  |
| rolloutStatuses | id | DefaultPaginator | ✅ |  ❌  |
| environments | id | DefaultPaginator | ✅ |  ❌  |
| trafficTypes | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| feature_flags | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-18 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>