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
| 0.0.4 | 2025-04-19 | [58154](https://github.com/airbytehq/airbyte/pull/58154) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57674](https://github.com/airbytehq/airbyte/pull/57674) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57044](https://github.com/airbytehq/airbyte/pull/57044) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57010](https://github.com/airbytehq/airbyte/pull/57010) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
