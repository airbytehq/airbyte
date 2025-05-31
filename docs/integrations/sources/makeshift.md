# Makeshift
Collect base data from Makeshift Scheduling SAAS.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_key` | `string` | Key.  |  |
| `client_secret` | `string` | Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Shift |  | DefaultPaginator | ✅ |  ❌  |
| Punch |  | DefaultPaginator | ✅ |  ❌  |
| BreakPunch |  | DefaultPaginator | ✅ |  ❌  |
| User |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-05-27 | | Initial release by [@maximenicol](https://github.com/maximenicol) via Connector Builder |

</details>
