# Mention
Mention is a Social Listening and Media Monitoring Tool.
This connector allows you to extract data from various Mention APIs such as Accounts , Alerts , Mentions , Statistics and others
Docs: https://dev.mention.com/current/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `stats_interval` | `string` | Statistics Interval. Periodicity of statistics returned. it may be daily(P1D), weekly(P1W) or monthly(P1M). | P1D |
| `stats_start_date` | `string` | Statistics Start Date.  |  |
| `stats_end_date` | `string` | Statistics End Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| alert | id | DefaultPaginator | ✅ |  ❌  |
| mention | id | DefaultPaginator | ✅ |  ❌  |
| mention_children | id | DefaultPaginator | ✅ |  ❌  |
| account_me | id | No pagination | ✅ |  ❌  |
| account | id | No pagination | ✅ |  ❌  |
| alert_tag | id | No pagination | ✅ |  ❌  |
| alert_author |  | DefaultPaginator | ✅ |  ❌  |
| alert_tasks | id | DefaultPaginator | ✅ |  ❌  |
| statistics |  | No pagination | ✅ |  ✅  |
| mention_tasks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-10-28 | [47538](https://github.com/airbytehq/airbyte/pull/47538) | Update dependencies |
| 0.0.1 | 2024-10-23 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
