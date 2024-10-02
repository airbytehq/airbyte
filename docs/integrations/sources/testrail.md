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
| 0.0.1 | 2024-09-29 | [46250](https://github.com/airbytehq/airbyte/pull/46250) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>