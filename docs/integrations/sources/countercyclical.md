# Countercyclical
Countercyclical is the fully end-to-end financial intelligence platform designed for modern investment teams.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Investments | id | No pagination | ✅ |  ❌  |
| Valuations | id | No pagination | ✅ |  ❌  |
| Memos | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-11-04 | [48283](https://github.com/airbytehq/airbyte/pull/48283) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47557](https://github.com/airbytehq/airbyte/pull/47557) | Update dependencies |
| 0.0.1 | 2024-10-06 | | Initial release by [@williamleiby](https://github.com/williamleiby) via Connector Builder |

</details>
