# Ramp
Syncs cards, transactions, and reimbursements from Ramp&#39;s developer API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Ramp Client ID. Client ID of the Ramp developer app (Ramp &gt; Company &gt; Developer). The app needs the Client Credentials grant and the scopes `transactions:read`, `cards:read` and `reimbursements:read`. |  |
| `client_secret` | `string` | Ramp Client Secret. Your Ramp API client secret. |  |
| `start_date` | `string` | Start Date. Only transactions and reimbursements changed on or after this date are synced on the first sync. Format ISO 8601 with Z suffix (e.g. 2024-01-01T00:00:00Z). | `2019-01-01T00:00:00Z` |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| cards | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |
| reimbursements | id | DefaultPaginator | ✅ |  ✅  |

## Limitations & troubleshooting

- The transactions and reimbursements streams filter by `updated_at` on the server (`updated_after`), so incremental syncs only read records changed since the last sync.
- The transactions stream requests `state=ALL`, so declined transactions are included alongside cleared and pending ones.
- Terminated cards are not included: Ramp's `/cards` endpoint hides them by default.
- Requests are throttled to stay under Ramp's published rate limit of 200 requests per 10-second window.
- The reimbursements stream syncs both directions: out-of-pocket reimbursements (BUSINESS_TO_USER) and repayments (USER_TO_BUSINESS).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-09-24 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | Surface Ramp auth and scope errors as config errors, filter transactions server-side with `updated_after`, include declined transactions, add rate-limit budget, declare missing fields, make `start_date` optional |
| 0.0.7 | 2026-09-22 | [86778](https://github.com/airbytehq/airbyte/pull/86778) | Update dependencies |
| 0.0.6 | 2026-09-15 | [86193](https://github.com/airbytehq/airbyte/pull/86193) | Update dependencies |
| 0.0.5 | 2026-09-08 | [85624](https://github.com/airbytehq/airbyte/pull/85624) | Update dependencies |
| 0.0.4 | 2026-08-18 | [84843](https://github.com/airbytehq/airbyte/pull/84843) | Add hidden configurable API base URL for sandbox testing |
| 0.0.3 | 2026-08-18 | [84721](https://github.com/airbytehq/airbyte/pull/84721) | Update dependencies |
| 0.0.2 | 2026-08-11 | [84077](https://github.com/airbytehq/airbyte/pull/84077) | Update dependencies |
| 0.0.1 | 2026-08-05 | [83706](https://github.com/airbytehq/airbyte/pull/83706) | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
