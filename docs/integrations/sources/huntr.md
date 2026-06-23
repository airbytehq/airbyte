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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.1.0 | 2025-01-29 | Add new streams |
| 0.0.1 | 2025-01-15 | Initial release by [@krokrob](https://github.com/krokrob) via Connector Builder|

</details>
