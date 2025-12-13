# Testrail
This directory contains the manifest-only connector for [`source-testrail`](https://www.testrail.com/).

## Documentation reference:
Visit `https://support.testrail.com/hc/en-us/articles/7077196481428-Attachments` for V1 API documentation

## Authentication setup
`Testrail` uses basic http authentication, Visit `https://support.testrail.com/hc/en-us/articles/7077039051284-Accessing-the-TestRail-API` for more info.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |
| `domain_name` | `string` | The unique domain name for accessing testrail.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | DefaultPaginator | ✅ |  ❌  |
| priorities | id | DefaultPaginator | ✅ |  ❌  |
| plans | id | DefaultPaginator | ✅ |  ✅  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| runs | id | DefaultPaginator | ✅ |  ✅  |
| result_fields | id | DefaultPaginator | ✅ |  ❌  |
| suites | id | DefaultPaginator | ✅ |  ❌  |
| templates | id | DefaultPaginator | ✅ |  ❌  |
| runs_tests | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| sections | id | DefaultPaginator | ✅ |  ❌  |
| case_statuses | case_status_id | DefaultPaginator | ✅ |  ❌  |
| milestones | id | DefaultPaginator | ✅ |  ✅  |
| datasets | id | DefaultPaginator | ✅ |  ❌  |
| configs | id | DefaultPaginator | ✅ |  ❌  |
| case_types | id | DefaultPaginator | ✅ |  ❌  |
| case_fields | id | DefaultPaginator | ✅ |  ❌  |
| cases | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | -- | ---------------- |
| 0.0.41 | 2025-12-09 | [70658](https://github.com/airbytehq/airbyte/pull/70658) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70051](https://github.com/airbytehq/airbyte/pull/70051) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69546](https://github.com/airbytehq/airbyte/pull/69546) | Update dependencies |
| 0.0.38 | 2025-10-29 | [69015](https://github.com/airbytehq/airbyte/pull/69015) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68491](https://github.com/airbytehq/airbyte/pull/68491) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67904](https://github.com/airbytehq/airbyte/pull/67904) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67461](https://github.com/airbytehq/airbyte/pull/67461) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66889](https://github.com/airbytehq/airbyte/pull/66889) | Update dependencies |
| 0.0.33 | 2025-09-23 | [66363](https://github.com/airbytehq/airbyte/pull/66363) | Update dependencies |
| 0.0.32 | 2025-09-09 | [66126](https://github.com/airbytehq/airbyte/pull/66126) | Update dependencies |
| 0.0.31 | 2025-08-24 | [65475](https://github.com/airbytehq/airbyte/pull/65475) | Update dependencies |
| 0.0.30 | 2025-08-16 | [65009](https://github.com/airbytehq/airbyte/pull/65009) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64465](https://github.com/airbytehq/airbyte/pull/64465) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63068](https://github.com/airbytehq/airbyte/pull/63068) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62725](https://github.com/airbytehq/airbyte/pull/62725) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62285](https://github.com/airbytehq/airbyte/pull/62285) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61293](https://github.com/airbytehq/airbyte/pull/61293) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60460](https://github.com/airbytehq/airbyte/pull/60460) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60093](https://github.com/airbytehq/airbyte/pull/60093) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59613](https://github.com/airbytehq/airbyte/pull/59613) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59028](https://github.com/airbytehq/airbyte/pull/59028) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58413](https://github.com/airbytehq/airbyte/pull/58413) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57974](https://github.com/airbytehq/airbyte/pull/57974) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57456](https://github.com/airbytehq/airbyte/pull/57456) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56824](https://github.com/airbytehq/airbyte/pull/56824) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56283](https://github.com/airbytehq/airbyte/pull/56283) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55573](https://github.com/airbytehq/airbyte/pull/55573) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55132](https://github.com/airbytehq/airbyte/pull/55132) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54527](https://github.com/airbytehq/airbyte/pull/54527) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54075](https://github.com/airbytehq/airbyte/pull/54075) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53563](https://github.com/airbytehq/airbyte/pull/53563) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53041](https://github.com/airbytehq/airbyte/pull/53041) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52447](https://github.com/airbytehq/airbyte/pull/52447) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51963](https://github.com/airbytehq/airbyte/pull/51963) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51454](https://github.com/airbytehq/airbyte/pull/51454) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50825](https://github.com/airbytehq/airbyte/pull/50825) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50352](https://github.com/airbytehq/airbyte/pull/50352) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49400](https://github.com/airbytehq/airbyte/pull/49400) | Update dependencies |
| 0.0.3 | 2024-11-04 | [47773](https://github.com/airbytehq/airbyte/pull/47773) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47630](https://github.com/airbytehq/airbyte/pull/47630) | Update dependencies |
| 0.0.1 | 2024-09-29 | [46250](https://github.com/airbytehq/airbyte/pull/46250) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
