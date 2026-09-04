# Ploomes
Ploomes CRM Source Connector (Declarative)

This connector provides native integration with the Ploomes CRM Public API, enabling continuous ingestion of entities such as Users, Products, and other CRM resources.

It is fully built using the Airbyte Connector Builder and implements:
- Pagination via $top and $skip
- Authentication using the User-Key header
- Incremental sync based on LastUpdateDate
- Automatic retry with exponential backoff
- Clean declarative schemas and reusable components

This connector is ideal for modern ELT pipelines, data lake ingestion, business analytics workflows, and integrations with Power BI, Snowflake, BigQuery, Databricks, and any destination supported by Airbyte.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_datetime` | `string` | Start datetime. ISO8601, ex: 2023-01-01T00:00:00.000-03:00 | 2024-01-01T00:00:00.000-03:00 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Users |  | DefaultPaginator | ✅ |  ✅  |
| Products |  | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-15 | | Initial release by [@felipelc](https://github.com/felipelc) via Connector Builder |

</details>
