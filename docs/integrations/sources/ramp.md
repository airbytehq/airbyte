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

## Limitations & troubleshooting

- The transactions stream filters by `updated_at` on the client side: every sync re-reads the full transaction list from the API and emits only new or updated records.
- Declined transactions are not included (Ramp API default).
- The reimbursements stream syncs both directions: out-of-pocket reimbursements (BUSINESS_TO_USER) and repayments (USER_TO_BUSINESS).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2026-08-18 | [84843](https://github.com/airbytehq/airbyte/pull/84843) | Add hidden configurable API base URL for sandbox testing |
| 0.0.3 | 2026-08-18 | [84721](https://github.com/airbytehq/airbyte/pull/84721) | Update dependencies |
| 0.0.2 | 2026-08-11 | [84077](https://github.com/airbytehq/airbyte/pull/84077) | Update dependencies |
| 0.0.1 | 2026-08-05 | [83706](https://github.com/airbytehq/airbyte/pull/83706) | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
