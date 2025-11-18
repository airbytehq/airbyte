# Interzoid Company Match API
This API provides a powerful mechanism for matching inconsistent company and organization name data within or across various data sources and datasets. It works by generating a similarity key using AI and specialized algorithms, so variations of the same organization name generate the same similarity key (GE, Gen Elec, GE Corp, etc.). Data can then be matched batched on similarity key rather than the organization name data itself for dramatically higher match rates.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| simkey |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-18 | | Initial release by [@interzoid](https://github.com/interzoid) via Connector Builder |

</details>
