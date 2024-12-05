# Split-io
This page contains the setup guide and reference information for the [Split-io](https://app.split.io/) source connector.

## Documentation reference:
Visit `https://docs.split.io/reference/introduction` for API documentation

## Authentication setup
Split uses bearer token authentication,
Refer `https://docs.split.io/reference/authentication` for more details.

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-18 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>