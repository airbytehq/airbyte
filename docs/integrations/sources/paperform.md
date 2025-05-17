# Paperform
Airbyte connector for [Paperform](https://paperform.co/) enables seamless data integration between Paperform and other platforms, allowing automated data synchronization and transfer from Paperform form submissions to your data warehouse or analytics tools. This connector helps streamline workflows by enabling data extraction, transformation, and loading (ETL) to leverage form data for insights and reporting across systems.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Generate it on your account page at https://paperform.co/account/developer. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | id | DefaultPaginator | ✅ |  ❌  |
| form_fields | key | DefaultPaginator | ✅ |  ❌  |
| submissions | id | DefaultPaginator | ✅ |  ❌  |
| partial_submissions | id | DefaultPaginator | ✅ |  ❌  |
| coupons | code | DefaultPaginator | ✅ |  ❌  |
| products |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.22 | 2025-05-17 | [60458](https://github.com/airbytehq/airbyte/pull/60458) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60192](https://github.com/airbytehq/airbyte/pull/60192) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59477](https://github.com/airbytehq/airbyte/pull/59477) | Update dependencies |
| 0.0.19 | 2025-04-27 | [59064](https://github.com/airbytehq/airbyte/pull/59064) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58501](https://github.com/airbytehq/airbyte/pull/58501) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57850](https://github.com/airbytehq/airbyte/pull/57850) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57332](https://github.com/airbytehq/airbyte/pull/57332) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56784](https://github.com/airbytehq/airbyte/pull/56784) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56215](https://github.com/airbytehq/airbyte/pull/56215) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55064](https://github.com/airbytehq/airbyte/pull/55064) | Update dependencies |
| 0.0.12 | 2025-02-23 | [54590](https://github.com/airbytehq/airbyte/pull/54590) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53987](https://github.com/airbytehq/airbyte/pull/53987) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53501](https://github.com/airbytehq/airbyte/pull/53501) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53014](https://github.com/airbytehq/airbyte/pull/53014) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52490](https://github.com/airbytehq/airbyte/pull/52490) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51853](https://github.com/airbytehq/airbyte/pull/51853) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51357](https://github.com/airbytehq/airbyte/pull/51357) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50240](https://github.com/airbytehq/airbyte/pull/50240) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49698](https://github.com/airbytehq/airbyte/pull/49698) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49370](https://github.com/airbytehq/airbyte/pull/49370) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49075](https://github.com/airbytehq/airbyte/pull/49075) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
