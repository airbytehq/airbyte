# Huntr
A connector for the Huntr application

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| members | id | DefaultPaginator | ✅ |  ❌  |
| organization_invitations | id | DefaultPaginator | ✅ |  ❌  |
| member_fields | id | DefaultPaginator | ✅ |  ❌  |
| activities | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| actions | id | DefaultPaginator | ✅ |  ❌  |
| candidates | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2025-01-15 | Initial release by [@krokrob](https://github.com/krokrob) via Connector Builder|

</details>