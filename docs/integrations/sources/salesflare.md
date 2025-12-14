# Salesflare
Salesflare is a CRM tool for small and medium businesses.
Using this connector we can extract data from various streams such as opportunities , workflows and pipelines.
Docs : https://api.salesflare.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Enter you api key like this : Bearer YOUR_API_KEY |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| persons | id | No pagination | ✅ |  ❌  |
| email data sources | id | No pagination | ✅ |  ❌  |
| custom field types | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70759](https://github.com/airbytehq/airbyte/pull/70759) | Update dependencies |
| 0.0.37 | 2025-11-25 | [69991](https://github.com/airbytehq/airbyte/pull/69991) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69699](https://github.com/airbytehq/airbyte/pull/69699) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68861](https://github.com/airbytehq/airbyte/pull/68861) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68403](https://github.com/airbytehq/airbyte/pull/68403) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67928](https://github.com/airbytehq/airbyte/pull/67928) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67215](https://github.com/airbytehq/airbyte/pull/67215) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66873](https://github.com/airbytehq/airbyte/pull/66873) | Update dependencies |
| 0.0.30 | 2025-09-23 | [66632](https://github.com/airbytehq/airbyte/pull/66632) | Update dependencies |
| 0.0.29 | 2025-09-09 | [66125](https://github.com/airbytehq/airbyte/pull/66125) | Update dependencies |
| 0.0.28 | 2025-08-23 | [65425](https://github.com/airbytehq/airbyte/pull/65425) | Update dependencies |
| 0.0.27 | 2025-08-16 | [65001](https://github.com/airbytehq/airbyte/pull/65001) | Update dependencies |
| 0.0.26 | 2025-08-02 | [64445](https://github.com/airbytehq/airbyte/pull/64445) | Update dependencies |
| 0.0.25 | 2025-07-19 | [63644](https://github.com/airbytehq/airbyte/pull/63644) | Update dependencies |
| 0.0.24 | 2025-07-05 | [62670](https://github.com/airbytehq/airbyte/pull/62670) | Update dependencies |
| 0.0.23 | 2025-06-28 | [62281](https://github.com/airbytehq/airbyte/pull/62281) | Update dependencies |
| 0.0.22 | 2025-06-21 | [61788](https://github.com/airbytehq/airbyte/pull/61788) | Update dependencies |
| 0.0.21 | 2025-05-24 | [60440](https://github.com/airbytehq/airbyte/pull/60440) | Update dependencies |
| 0.0.20 | 2025-05-10 | [60096](https://github.com/airbytehq/airbyte/pull/60096) | Update dependencies |
| 0.0.19 | 2025-05-04 | [58983](https://github.com/airbytehq/airbyte/pull/58983) | Update dependencies |
| 0.0.18 | 2025-04-19 | [57980](https://github.com/airbytehq/airbyte/pull/57980) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57458](https://github.com/airbytehq/airbyte/pull/57458) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56751](https://github.com/airbytehq/airbyte/pull/56751) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56212](https://github.com/airbytehq/airbyte/pull/56212) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55051](https://github.com/airbytehq/airbyte/pull/55051) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54568](https://github.com/airbytehq/airbyte/pull/54568) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53948](https://github.com/airbytehq/airbyte/pull/53948) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53489](https://github.com/airbytehq/airbyte/pull/53489) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52960](https://github.com/airbytehq/airbyte/pull/52960) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52486](https://github.com/airbytehq/airbyte/pull/52486) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51918](https://github.com/airbytehq/airbyte/pull/51918) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51311](https://github.com/airbytehq/airbyte/pull/51311) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50695](https://github.com/airbytehq/airbyte/pull/50695) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50234](https://github.com/airbytehq/airbyte/pull/50234) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49660](https://github.com/airbytehq/airbyte/pull/49660) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49325](https://github.com/airbytehq/airbyte/pull/49325) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49078](https://github.com/airbytehq/airbyte/pull/49078) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
