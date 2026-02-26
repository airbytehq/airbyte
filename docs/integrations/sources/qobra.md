# Qobra
This connector is designed to load datas from Qobra into your data warehouse.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key.  |  |
| `start_date` | `string` | start_date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| structure_statement_reporting |  | No pagination | ✅ |  ❌  |
| structure_record_reporting |  | No pagination | ✅ |  ❌  |
| statement_reporting | standard.id | DefaultPaginator | ✅ |  ✅  |
| record_reporting | standard.id | DefaultPaginator | ✅ |  ✅  |
| data_structure |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-02-26 | | Initial release by [@NicolasQobra](https://github.com/NicolasQobra) via Connector Builder |

</details>
