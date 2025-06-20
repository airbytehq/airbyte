# WeFact
WeFact invoicing

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Invoices | Identifier | No pagination | ✅ |  ❌  |
| Customers | Identifier | No pagination | ✅ |  ❌  |
| Subscriptions | Identifier | No pagination | ✅ |  ❌  |
| Products | Identifier | No pagination | ✅ |  ❌  |
| Quotes | Identifier | No pagination | ✅ |  ❌  |
| Suppliers | Identifier | No pagination | ✅ |  ❌  |
| Credit invoices | Identifier | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-06-20 | | Initial release by [@marcelrummens](https://github.com/marcelrummens) via Connector Builder |

</details>
