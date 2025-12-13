# Thrive Learning
A Connector for Thrive Learning

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Tenant ID. Your website Tenant ID (eu-west-000000 please contact support for your tenant) |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Content | id | DefaultPaginator | ✅ |  ❌  |
| Users | id | DefaultPaginator | ✅ |  ❌  |
| Activities | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.20 | 2025-12-09 | [70735](https://github.com/airbytehq/airbyte/pull/70735) | Update dependencies |
| 0.0.19 | 2025-11-25 | [69852](https://github.com/airbytehq/airbyte/pull/69852) | Update dependencies |
| 0.0.18 | 2025-11-18 | [69662](https://github.com/airbytehq/airbyte/pull/69662) | Update dependencies |
| 0.0.17 | 2025-10-29 | [69038](https://github.com/airbytehq/airbyte/pull/69038) | Update dependencies |
| 0.0.16 | 2025-10-21 | [68536](https://github.com/airbytehq/airbyte/pull/68536) | Update dependencies |
| 0.0.15 | 2025-10-14 | [67869](https://github.com/airbytehq/airbyte/pull/67869) | Update dependencies |
| 0.0.14 | 2025-10-07 | [67466](https://github.com/airbytehq/airbyte/pull/67466) | Update dependencies |
| 0.0.13 | 2025-09-30 | [66884](https://github.com/airbytehq/airbyte/pull/66884) | Update dependencies |
| 0.0.12 | 2025-09-23 | [66357](https://github.com/airbytehq/airbyte/pull/66357) | Update dependencies |
| 0.0.11 | 2025-09-09 | [66113](https://github.com/airbytehq/airbyte/pull/66113) | Update dependencies |
| 0.0.10 | 2025-08-24 | [65437](https://github.com/airbytehq/airbyte/pull/65437) | Update dependencies |
| 0.0.9 | 2025-08-16 | [65022](https://github.com/airbytehq/airbyte/pull/65022) | Update dependencies |
| 0.0.8 | 2025-08-02 | [64410](https://github.com/airbytehq/airbyte/pull/64410) | Update dependencies |
| 0.0.7 | 2025-07-12 | [63059](https://github.com/airbytehq/airbyte/pull/63059) | Update dependencies |
| 0.0.6 | 2025-07-05 | [62731](https://github.com/airbytehq/airbyte/pull/62731) | Update dependencies |
| 0.0.5 | 2025-06-28 | [62254](https://github.com/airbytehq/airbyte/pull/62254) | Update dependencies |
| 0.0.4 | 2025-06-21 | [61794](https://github.com/airbytehq/airbyte/pull/61794) | Update dependencies |
| 0.0.3 | 2025-06-14 | [61612](https://github.com/airbytehq/airbyte/pull/61612) | Update dependencies |
| 0.0.2 | 2025-05-25 | [60447](https://github.com/airbytehq/airbyte/pull/60447) | Update dependencies |
| 0.0.1 | 2025-05-16 | | Initial release by [@cjm-s](https://github.com/cjm-s) via Connector Builder |

</details>
