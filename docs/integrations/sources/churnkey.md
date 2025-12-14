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
| 0.0.18 | 2025-12-09 | [70626](https://github.com/airbytehq/airbyte/pull/70626) | Update dependencies |
| 0.0.17 | 2025-11-25 | [69906](https://github.com/airbytehq/airbyte/pull/69906) | Update dependencies |
| 0.0.16 | 2025-11-18 | [69633](https://github.com/airbytehq/airbyte/pull/69633) | Update dependencies |
| 0.0.15 | 2025-10-29 | [68859](https://github.com/airbytehq/airbyte/pull/68859) | Update dependencies |
| 0.0.14 | 2025-10-21 | [68511](https://github.com/airbytehq/airbyte/pull/68511) | Update dependencies |
| 0.0.13 | 2025-10-14 | [68052](https://github.com/airbytehq/airbyte/pull/68052) | Update dependencies |
| 0.0.12 | 2025-10-07 | [67192](https://github.com/airbytehq/airbyte/pull/67192) | Update dependencies |
| 0.0.11 | 2025-09-30 | [65810](https://github.com/airbytehq/airbyte/pull/65810) | Update dependencies |
| 0.0.10 | 2025-08-23 | [65258](https://github.com/airbytehq/airbyte/pull/65258) | Update dependencies |
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
