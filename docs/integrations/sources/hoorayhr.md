# HoorayHR
Source connector for HoorayHR (https://hoorayhr.io). The connector uses https://api.hoorayhr.io

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `hoorayhrpassword` | `string` | HoorayHR Password.  |  |
| `hoorayhrusername` | `string` | HoorayHR Username.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| sick-leaves | id | No pagination | ✅ |  ❌  |
| time-off | id | No pagination | ✅ |  ❌  |
| leave-types | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-12-17 | | Initial release by [@JoeriSmits](https://github.com/JoeriSmits) via Connector Builder |

</details>
