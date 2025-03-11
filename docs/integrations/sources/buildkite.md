# Buildkite
This page contains the setup guide and reference information for the [Buildkite](https://buildkite.com/) source connector.

## Documentation reference:
Visit `https://buildkite.com/docs/apis/rest-api` for API documentation

## Authentication setup
Buildkite uses bearer token authentication,
Visit `https://buildkite.com/user/api-access-tokens` for getting your bearer token.

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.15 | 2025-03-08 | [55382](https://github.com/airbytehq/airbyte/pull/55382) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54898](https://github.com/airbytehq/airbyte/pull/54898) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54213](https://github.com/airbytehq/airbyte/pull/54213) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53876](https://github.com/airbytehq/airbyte/pull/53876) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53432](https://github.com/airbytehq/airbyte/pull/53432) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52927](https://github.com/airbytehq/airbyte/pull/52927) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52188](https://github.com/airbytehq/airbyte/pull/52188) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51715](https://github.com/airbytehq/airbyte/pull/51715) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51226](https://github.com/airbytehq/airbyte/pull/51226) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50485](https://github.com/airbytehq/airbyte/pull/50485) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50205](https://github.com/airbytehq/airbyte/pull/50205) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49590](https://github.com/airbytehq/airbyte/pull/49590) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49010](https://github.com/airbytehq/airbyte/pull/49010) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47476](https://github.com/airbytehq/airbyte/pull/47476) | Update dependencies |
| 0.0.1 | 2024-09-11 | [45384](https://github.com/airbytehq/airbyte/pull/45384) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
