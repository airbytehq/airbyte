# GoLogin
Website: https://app.gologin.com/
Postman API Reference: https://documenter.getpostman.com/view/21126834/Uz5GnvaL#intro

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API Key found at `https://app.gologin.com/personalArea/TokenApi` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| profiles | id | DefaultPaginator | ✅ |  ✅  |
| browser_history | id | DefaultPaginator | ✅ |  ✅  |
| browser_cookies | uuid | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| tags | _id | DefaultPaginator | ✅ |  ❌  |
| user | _id | DefaultPaginator | ✅ |  ✅  |
| user_metadata | _id | DefaultPaginator | ✅ |  ✅  |
| user_balance | uuid | DefaultPaginator | ✅ |  ❌  |
| user_timezones | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-04 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
