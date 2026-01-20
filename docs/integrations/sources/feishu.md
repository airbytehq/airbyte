# Feishu
Extracts data from Feishu/Lark Bitable (Base). Supports authentication via App ID and App Secret.

**Prerequisites:**
1. A Feishu/Lark account.
2. A custom app created in the Feishu Open Platform with Bitable permissions enabled.
3. The App ID and App Secret.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `app_id` | `string` | App Id.  |  |
| `table_id` | `string` | Table Id.  |  |
| `app_token` | `string` | App Token.  |  |
| `lark_host` | `string` | Lark Host.  | https://open.feishu.cn |
| `page_size` | `number` | Page Size.  | 100 |
| `app_secret` | `string` | App Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| records | record_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-01-09 | | Initial release by [@WYW-min](https://github.com/WYW-min) via Connector Builder |

</details>
