# Google Calendar
Solves https://github.com/airbytehq/airbyte/issues/45995

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token_2` | `string` | Refresh token.  |  |
| `calendarid` | `string` | Calendar Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| colors | calendar.event | No pagination | ✅ |  ❌  |
| settings | id | DefaultPaginator | ✅ |  ❌  |
| calendarlist | id | DefaultPaginator | ✅ |  ❌  |
| calendars | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.31 | 2025-12-09 | [70696](https://github.com/airbytehq/airbyte/pull/70696) | Update dependencies |
| 0.0.30 | 2025-11-25 | [69889](https://github.com/airbytehq/airbyte/pull/69889) | Update dependencies |
| 0.0.29 | 2025-11-18 | [69373](https://github.com/airbytehq/airbyte/pull/69373) | Update dependencies |
| 0.0.28 | 2025-10-29 | [69049](https://github.com/airbytehq/airbyte/pull/69049) | Update dependencies |
| 0.0.27 | 2025-10-21 | [68310](https://github.com/airbytehq/airbyte/pull/68310) | Update dependencies |
| 0.0.26 | 2025-10-14 | [68007](https://github.com/airbytehq/airbyte/pull/68007) | Update dependencies |
| 0.0.25 | 2025-10-07 | [67257](https://github.com/airbytehq/airbyte/pull/67257) | Update dependencies |
| 0.0.24 | 2025-09-30 | [66309](https://github.com/airbytehq/airbyte/pull/66309) | Update dependencies |
| 0.0.23 | 2025-09-09 | [66046](https://github.com/airbytehq/airbyte/pull/66046) | Update dependencies |
| 0.0.22 | 2025-08-23 | [65366](https://github.com/airbytehq/airbyte/pull/65366) | Update dependencies |
| 0.0.21 | 2025-08-09 | [64614](https://github.com/airbytehq/airbyte/pull/64614) | Update dependencies |
| 0.0.20 | 2025-08-02 | [64218](https://github.com/airbytehq/airbyte/pull/64218) | Update dependencies |
| 0.0.19 | 2025-07-26 | [63813](https://github.com/airbytehq/airbyte/pull/63813) | Update dependencies |
| 0.0.18 | 2025-07-19 | [63491](https://github.com/airbytehq/airbyte/pull/63491) | Update dependencies |
| 0.0.17 | 2025-07-12 | [63149](https://github.com/airbytehq/airbyte/pull/63149) | Update dependencies |
| 0.0.16 | 2025-07-05 | [62653](https://github.com/airbytehq/airbyte/pull/62653) | Update dependencies |
| 0.0.15 | 2025-06-28 | [62156](https://github.com/airbytehq/airbyte/pull/62156) | Update dependencies |
| 0.0.14 | 2025-06-21 | [61833](https://github.com/airbytehq/airbyte/pull/61833) | Update dependencies |
| 0.0.13 | 2025-06-14 | [61121](https://github.com/airbytehq/airbyte/pull/61121) | Update dependencies |
| 0.0.12 | 2025-05-24 | [60587](https://github.com/airbytehq/airbyte/pull/60587) | Update dependencies |
| 0.0.11 | 2025-05-10 | [59250](https://github.com/airbytehq/airbyte/pull/59250) | Update dependencies |
| 0.0.10 | 2025-04-26 | [58812](https://github.com/airbytehq/airbyte/pull/58812) | Update dependencies |
| 0.0.9 | 2025-04-19 | [58175](https://github.com/airbytehq/airbyte/pull/58175) | Update dependencies |
| 0.0.8 | 2025-04-12 | [57066](https://github.com/airbytehq/airbyte/pull/57066) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56487](https://github.com/airbytehq/airbyte/pull/56487) | Update dependencies |
| 0.0.6 | 2025-03-22 | [55939](https://github.com/airbytehq/airbyte/pull/55939) | Update dependencies |
| 0.0.5 | 2025-03-08 | [55325](https://github.com/airbytehq/airbyte/pull/55325) | Update dependencies |
| 0.0.4 | 2025-03-01 | [54992](https://github.com/airbytehq/airbyte/pull/54992) | Update dependencies |
| 0.0.3 | 2025-02-22 | [54395](https://github.com/airbytehq/airbyte/pull/54395) | Update dependencies |
| 0.0.2 | 2025-02-15 | [47915](https://github.com/airbytehq/airbyte/pull/47915) | Update dependencies |
| 0.0.1 | 2024-10-06 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
