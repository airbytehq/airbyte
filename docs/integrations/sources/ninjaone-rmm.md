# NinjaOne RMM
Website: https://app.ninjarmm.com/
API Reference: https://app.ninjarmm.com/apidocs/?links.active=core

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Token could be generated natively by authorize section of NinjaOne swagger documentation `https://app.ninjarmm.com/apidocs/?links.active=authorization` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| policies | id | No pagination | ✅ |  ✅  |
| activities | id | DefaultPaginator | ✅ |  ✅  |
| automation_scripts | id | No pagination | ✅ |  ✅  |
| groups | id | No pagination | ✅ |  ✅  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | No pagination | ✅ |  ✅  |
| software_products | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-04 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
