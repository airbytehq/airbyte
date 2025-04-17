# OPUSWatch
Connect to your OPUS data

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `initial_data` | `string` | Initial Data.  | 20250101 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| client |  | No pagination | ✅ |  ❌  |
| locations |  | No pagination | ✅ |  ❌  |
| rows |  | No pagination | ✅ |  ❌  |
| users |  | No pagination | ✅ |  ❌  |
| workers |  | No pagination | ✅ |  ❌  |
| worker groups |  | No pagination | ✅ |  ❌  |
| tasks |  | No pagination | ✅ |  ❌  |
| task groups |  | No pagination | ✅ |  ❌  |
| labels |  | No pagination | ✅ |  ❌  |
| varieties |  | No pagination | ✅ |  ❌  |
| registrations initial |  | DefaultPaginator | ✅ |  ❌  |
| registrations incremental |  | No pagination | ✅ |  ❌  |
| sessions initial |  | DefaultPaginator | ✅ |  ❌  |
| sessions incremental |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-17 | | Initial release by [@SebasZwinkels](https://github.com/SebasZwinkels) via Connector Builder |

</details>
