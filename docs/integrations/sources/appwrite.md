# Appwrite
Appwrite connector enables seamless data synchronization between Appwrite and other platforms. This connector simplifies integration by automating data flow and ensuring efficient data transfer across systems.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |
| `key_value` | `string` | Key Value.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | $id | DefaultPaginator | ✅ |  ❌  |
| teams | $id | DefaultPaginator | ✅ |  ❌  |
| team_memberships | $id | DefaultPaginator | ✅ |  ❌  |
| databases | $id | No pagination | ✅ |  ❌  |
| collections | $id | No pagination | ✅ |  ❌  |
| attributes | key | No pagination | ✅ |  ❌  |
| documents | $id | DefaultPaginator | ✅ |  ❌  |
| indexes | key | No pagination | ✅ |  ❌  |
| buckets | $id | No pagination | ✅ |  ❌  |
| files | $id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
