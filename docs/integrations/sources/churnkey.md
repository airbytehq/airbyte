# churnkey
connects to churnkey to retrieve session details

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `x-ck-app` | `string` | App ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| sessions |  | No pagination | ✅ |  ❌  |
| session-aggregation |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-08-09 | [64672](https://github.com/airbytehq/airbyte/pull/64672) | Update dependencies |
| 0.0.8 | 2025-08-02 | [64338](https://github.com/airbytehq/airbyte/pull/64338) | Update dependencies |
| 0.0.7 | 2025-07-26 | [63944](https://github.com/airbytehq/airbyte/pull/63944) | Update dependencies |
| 0.0.6 | 2025-07-19 | [63557](https://github.com/airbytehq/airbyte/pull/63557) | Update dependencies |
| 0.0.5 | 2025-07-12 | [63017](https://github.com/airbytehq/airbyte/pull/63017) | Update dependencies |
| 0.0.4 | 2025-07-05 | [62773](https://github.com/airbytehq/airbyte/pull/62773) | Update dependencies |
| 0.0.3 | 2025-06-28 | [62379](https://github.com/airbytehq/airbyte/pull/62379) | Update dependencies |
| 0.0.2 | 2025-06-21 | [61976](https://github.com/airbytehq/airbyte/pull/61976) | Update dependencies |
| 0.0.1 | 2025-06-18 | | Initial release by [@shdanielsh-nyk](https://github.com/shdanielsh-nyk) via Connector Builder |

</details>
