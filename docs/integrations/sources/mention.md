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
| 0.0.44 | 2025-12-09 | [70768](https://github.com/airbytehq/airbyte/pull/70768) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70121](https://github.com/airbytehq/airbyte/pull/70121) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69570](https://github.com/airbytehq/airbyte/pull/69570) | Update dependencies |
| 0.0.41 | 2025-10-29 | [69064](https://github.com/airbytehq/airbyte/pull/69064) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68467](https://github.com/airbytehq/airbyte/pull/68467) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67822](https://github.com/airbytehq/airbyte/pull/67822) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67390](https://github.com/airbytehq/airbyte/pull/67390) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66351](https://github.com/airbytehq/airbyte/pull/66351) | Update dependencies |
| 0.0.36 | 2025-09-09 | [65833](https://github.com/airbytehq/airbyte/pull/65833) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65193](https://github.com/airbytehq/airbyte/pull/65193) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64696](https://github.com/airbytehq/airbyte/pull/64696) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64280](https://github.com/airbytehq/airbyte/pull/64280) | Update dependencies |
| 0.0.32 | 2025-07-26 | [63911](https://github.com/airbytehq/airbyte/pull/63911) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63389](https://github.com/airbytehq/airbyte/pull/63389) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63251](https://github.com/airbytehq/airbyte/pull/63251) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62662](https://github.com/airbytehq/airbyte/pull/62662) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62328](https://github.com/airbytehq/airbyte/pull/62328) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61894](https://github.com/airbytehq/airbyte/pull/61894) | Update dependencies |
| 0.0.26 | 2025-06-14 | [61123](https://github.com/airbytehq/airbyte/pull/61123) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60594](https://github.com/airbytehq/airbyte/pull/60594) | Update dependencies |
| 0.0.24 | 2025-05-10 | [59844](https://github.com/airbytehq/airbyte/pull/59844) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59249](https://github.com/airbytehq/airbyte/pull/59249) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58806](https://github.com/airbytehq/airbyte/pull/58806) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58161](https://github.com/airbytehq/airbyte/pull/58161) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57682](https://github.com/airbytehq/airbyte/pull/57682) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57053](https://github.com/airbytehq/airbyte/pull/57053) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56033](https://github.com/airbytehq/airbyte/pull/56033) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55461](https://github.com/airbytehq/airbyte/pull/55461) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54830](https://github.com/airbytehq/airbyte/pull/54830) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54334](https://github.com/airbytehq/airbyte/pull/54334) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53826](https://github.com/airbytehq/airbyte/pull/53826) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53290](https://github.com/airbytehq/airbyte/pull/53290) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52758](https://github.com/airbytehq/airbyte/pull/52758) | Update dependencies |
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
