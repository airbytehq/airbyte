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
| 0.0.11 | 2025-01-25 | [52241](https://github.com/airbytehq/airbyte/pull/52241) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51795](https://github.com/airbytehq/airbyte/pull/51795) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51180](https://github.com/airbytehq/airbyte/pull/51180) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50607](https://github.com/airbytehq/airbyte/pull/50607) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50107](https://github.com/airbytehq/airbyte/pull/50107) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49601](https://github.com/airbytehq/airbyte/pull/49601) | Update dependencies |
| 0.0.5 | 2024-12-12 | [48998](https://github.com/airbytehq/airbyte/pull/48998) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48258](https://github.com/airbytehq/airbyte/pull/48258) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47841](https://github.com/airbytehq/airbyte/pull/47841) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47538](https://github.com/airbytehq/airbyte/pull/47538) | Update dependencies |
| 0.0.1 | 2024-10-23 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
