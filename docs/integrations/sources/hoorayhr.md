# HoorayHR
Source connector for HoorayHR (https://hoorayhr.io). The connector uses https://api.hoorayhr.io

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `hoorayhrusername` | `string` | HoorayHR Username.  |  |
| `hoorayhrpassword` | `string` | HoorayHR Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Sick Leaves | id | No pagination | ✅ |  ❌  |
| Time Off | id | No pagination | ✅ |  ❌  |
| Leave Types | id | No pagination | ✅ |  ❌  |
| Users | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-12-17 | | Initial release by [@JoeriSmits](https://github.com/JoeriSmits) via Connector Builder |

</details>
