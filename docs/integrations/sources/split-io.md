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
| 0.0.6 | 2025-01-11 | [51425](https://github.com/airbytehq/airbyte/pull/51425) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50791](https://github.com/airbytehq/airbyte/pull/50791) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50320](https://github.com/airbytehq/airbyte/pull/50320) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49735](https://github.com/airbytehq/airbyte/pull/49735) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49402](https://github.com/airbytehq/airbyte/pull/49402) | Update dependencies |
| 0.0.1 | 2024-09-18 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
