# Ramp
Syncs cards, transactions, and reimbursements from Ramp&#39;s developer API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Ramp Client ID. Your Ramp API client ID, created in Ramp&#39;s developer settings. |  |
| `client_secret` | `string` | Ramp Client Secret. Your Ramp API client secret. |  |
| `start_date` | `string` | Start Date. Earliest updated_at to pull on the initial sync of the transactions and reimbursements streams. Format ISO 8601 with Z suffix (e.g. 2024-01-01T00:00:00Z). Ignored on subsequent incremental syncs. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| cards | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |
| reimbursements | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-08-05 | | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
