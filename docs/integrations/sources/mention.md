# Mention
Mention is a Social Listening and Media Monitoring Tool.
This connector allows you to extract data from various Mention APIs such as Accounts , Alerts , Mentions , Statistics and others
Docs: https://dev.mention.com/current/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `from` | `string` | from. stats are to be fetched for mentions retrieved after that date |  |
| `to` | `string` | to. stats are fetched for mentions retrieved before that date |  |
| `interval` | `string` | interval. Periodicity of statistics returned. it may be daily(P1D), weekly(P1W) or monthly(P1M). | P1D |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Alerts | id | DefaultPaginator | ✅ |  ❌  |
| Alert | id | No pagination | ✅ |  ❌  |
| Mentions | id | DefaultPaginator | ✅ |  ❌  |
| Mention | id | No pagination | ✅ |  ❌  |
| Mention Children |  | DefaultPaginator | ✅ |  ❌  |
| Accounts | id | No pagination | ✅ |  ❌  |
| Account | id | No pagination | ✅ |  ❌  |
| Tags |  | No pagination | ✅ |  ❌  |
| Alert Authors |  | DefaultPaginator | ✅ |  ❌  |
| Alert Tasks |  | DefaultPaginator | ✅ |  ❌  |
| Statistics |  | No pagination | ✅ |  ❌  |
| Tasks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-12 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
