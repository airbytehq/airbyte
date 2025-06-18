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
| 0.0.1 | 2025-06-18 | | Initial release by [@shdanielsh-nyk](https://github.com/shdanielsh-nyk) via Connector Builder |

</details>
