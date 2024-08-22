# DBT

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | Token.  |  |
| `account_id` | `string` | account_id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| runs | id | DefaultPaginator | ✅ |  ❌  |

| projects | id | DefaultPaginator | ✅ |  ❌  |

| repositories | id | DefaultPaginator | ✅ |  ❌  |

| users | id | DefaultPaginator | ✅ |  ❌  |

| environments | id | DefaultPaginator | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-22 | Initial release by natikgadzhi via Connector Builder|

</details>