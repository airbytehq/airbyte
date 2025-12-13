# Zoho Bigin
 Zoho Bigin connector  enables seamless data sync between Zoho Bigin and other platforms. This connector automates CRM data integration, improving workflows and ensuring real-time access to customer insights across tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `data_center` | `string` | Data Center. The data center where the Bigin account's resources are hosted | com |
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | No pagination | ✅ |  ❌  |
| organizations | id | No pagination | ✅ |  ❌  |
| roles | id | No pagination | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| tasks |  | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.42 | 2025-12-09 | [70728](https://github.com/airbytehq/airbyte/pull/70728) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70077](https://github.com/airbytehq/airbyte/pull/70077) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69515](https://github.com/airbytehq/airbyte/pull/69515) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68985](https://github.com/airbytehq/airbyte/pull/68985) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68404](https://github.com/airbytehq/airbyte/pull/68404) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67993](https://github.com/airbytehq/airbyte/pull/67993) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67245](https://github.com/airbytehq/airbyte/pull/67245) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66853](https://github.com/airbytehq/airbyte/pull/66853) | Update dependencies |
| 0.0.34 | 2025-09-24 | [66466](https://github.com/airbytehq/airbyte/pull/66466) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65732](https://github.com/airbytehq/airbyte/pull/65732) | Update dependencies |
| 0.0.32 | 2025-08-24 | [65480](https://github.com/airbytehq/airbyte/pull/65480) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64853](https://github.com/airbytehq/airbyte/pull/64853) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64346](https://github.com/airbytehq/airbyte/pull/64346) | Update dependencies |
| 0.0.29 | 2025-07-26 | [64074](https://github.com/airbytehq/airbyte/pull/64074) | Update dependencies |
| 0.0.28 | 2025-07-20 | [63691](https://github.com/airbytehq/airbyte/pull/63691) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63228](https://github.com/airbytehq/airbyte/pull/63228) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62674](https://github.com/airbytehq/airbyte/pull/62674) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62236](https://github.com/airbytehq/airbyte/pull/62236) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61767](https://github.com/airbytehq/airbyte/pull/61767) | Update dependencies |
| 0.0.23 | 2025-06-15 | [61258](https://github.com/airbytehq/airbyte/pull/61258) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60749](https://github.com/airbytehq/airbyte/pull/60749) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59913](https://github.com/airbytehq/airbyte/pull/59913) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59538](https://github.com/airbytehq/airbyte/pull/59538) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58939](https://github.com/airbytehq/airbyte/pull/58939) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58558](https://github.com/airbytehq/airbyte/pull/58558) | Update dependencies |
| 0.0.17 | 2025-04-12 | [58033](https://github.com/airbytehq/airbyte/pull/58033) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57392](https://github.com/airbytehq/airbyte/pull/57392) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56819](https://github.com/airbytehq/airbyte/pull/56819) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56329](https://github.com/airbytehq/airbyte/pull/56329) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55661](https://github.com/airbytehq/airbyte/pull/55661) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55158](https://github.com/airbytehq/airbyte/pull/55158) | Update dependencies |
| 0.0.11 | 2025-02-23 | [54627](https://github.com/airbytehq/airbyte/pull/54627) | Update dependencies |
| 0.0.10 | 2025-02-15 | [54118](https://github.com/airbytehq/airbyte/pull/54118) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53592](https://github.com/airbytehq/airbyte/pull/53592) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53124](https://github.com/airbytehq/airbyte/pull/53124) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52544](https://github.com/airbytehq/airbyte/pull/52544) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51936](https://github.com/airbytehq/airbyte/pull/51936) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51472](https://github.com/airbytehq/airbyte/pull/51472) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50832](https://github.com/airbytehq/airbyte/pull/50832) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50391](https://github.com/airbytehq/airbyte/pull/50391) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49449](https://github.com/airbytehq/airbyte/pull/49449) | Update dependencies |
| 0.0.1 | 2024-10-27 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
