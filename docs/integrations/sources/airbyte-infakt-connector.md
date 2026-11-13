# Airbyte Infakt Connector
InFakt is a Polish invoicing and accounting SaaS platform used by businesses to manage invoices, clients, and financial documents. This connector enables automated extraction of invoice and client data
from InFakt into your data warehouse.

The connector supports:
- **Clients stream**: Complete client/company directory with contact information and tax IDs (NIP)
- **Invoices stream**: Comprehensive invoice data including financial details, payment status, and client references with incremental sync support

Key features:
- Incremental sync based on invoice date for efficient data replication
- Automatic pagination handling for large datasets
- Robust error handling with exponential backoff for rate limits
- Configurable date ranges for historical data backfills

This connector is ideal for businesses using InFakt who need to:
- Build financial reporting dashboards in BI tools
- Integrate invoice data with ERP or accounting systems
- Perform revenue analysis and forecasting
- Track accounts receivable and payment status
- Consolidate data from multiple legal entities

Authentication requires an InFakt API key which can be obtained from the InFakt application settings.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. InFakt API Key (X-inFakt-ApiKey) for authentication. Get it from https://app.infakt.pl/app/ustawienia/integracja.html |  |
| `end_date` | `string` | End Date. End date for incremental invoice sync (YYYY-MM-DD). Defaults to current date if not provided. |  |
| `start_date` | `string` | Start Date. Start date for incremental invoice sync (YYYY-MM-DD). Only invoices with invoice_date &gt;= this date will be synced. Defaults to 90 days ago if not provided. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| clients | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-10-16 | | Initial release by [@emilwojtaszek](https://github.com/emilwojtaszek) via Connector Builder |

</details>
