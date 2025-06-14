# Drip
Integrate seamlessly with Drip using this Airbyte connector, enabling smooth data sync for all your email marketing needs. Effortlessly connect and automate data flows to optimize your marketing strategies with ease

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://www.getdrip.com/user/edit |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| broadcasts | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| users | email | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | custom_field_identifiers | DefaultPaginator | ✅ |  ❌  |
| conversions | id | DefaultPaginator | ✅ |  ❌  |
| events | account_id | DefaultPaginator | ✅ |  ❌  |
| tags | tags | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.26 | 2025-06-14 | [61271](https://github.com/airbytehq/airbyte/pull/61271) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60386](https://github.com/airbytehq/airbyte/pull/60386) | Update dependencies |
| 0.0.24 | 2025-05-10 | [59949](https://github.com/airbytehq/airbyte/pull/59949) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59412](https://github.com/airbytehq/airbyte/pull/59412) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58832](https://github.com/airbytehq/airbyte/pull/58832) | Update dependencies |
| 0.0.21 | 2025-04-19 | [57833](https://github.com/airbytehq/airbyte/pull/57833) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57199](https://github.com/airbytehq/airbyte/pull/57199) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56547](https://github.com/airbytehq/airbyte/pull/56547) | Update dependencies |
| 0.0.18 | 2025-03-22 | [55917](https://github.com/airbytehq/airbyte/pull/55917) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55316](https://github.com/airbytehq/airbyte/pull/55316) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54957](https://github.com/airbytehq/airbyte/pull/54957) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54375](https://github.com/airbytehq/airbyte/pull/54375) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53724](https://github.com/airbytehq/airbyte/pull/53724) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53355](https://github.com/airbytehq/airbyte/pull/53355) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52807](https://github.com/airbytehq/airbyte/pull/52807) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52375](https://github.com/airbytehq/airbyte/pull/52375) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51683](https://github.com/airbytehq/airbyte/pull/51683) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51132](https://github.com/airbytehq/airbyte/pull/51132) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50528](https://github.com/airbytehq/airbyte/pull/50528) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50042](https://github.com/airbytehq/airbyte/pull/50042) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49531](https://github.com/airbytehq/airbyte/pull/49531) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49204](https://github.com/airbytehq/airbyte/pull/49204) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48914](https://github.com/airbytehq/airbyte/pull/48914) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48311](https://github.com/airbytehq/airbyte/pull/48311) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47446](https://github.com/airbytehq/airbyte/pull/47446) | Update dependencies |
| 0.0.1 | 2024-10-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
