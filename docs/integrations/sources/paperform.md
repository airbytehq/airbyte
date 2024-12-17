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
| 0.0.4 | 2024-12-14 | [49698](https://github.com/airbytehq/airbyte/pull/49698) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49370](https://github.com/airbytehq/airbyte/pull/49370) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49075](https://github.com/airbytehq/airbyte/pull/49075) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
