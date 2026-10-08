# Ramp
Syncs cards, transactions and reimbursements, plus Ramp&#39;s organisation, spend-control, accounts-payable and procurement data, from Ramp&#39;s developer API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Ramp Client ID. Your Ramp API client ID, created in Ramp&#39;s developer settings. |  |
| `client_secret` | `string` | Ramp Client Secret. Your Ramp API client secret. |  |
| `start_date` | `string` | Start Date. Earliest updated_at to pull on the initial sync of the transactions and reimbursements streams, and earliest created_at for the receipts stream. Format ISO 8601 with Z suffix (e.g. 2024-01-01T00:00:00Z). Ignored on subsequent incremental syncs. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| cards | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |
| reimbursements | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| departments | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| entities | id | DefaultPaginator | ✅ |  ❌  |
| business | id | No pagination | ✅ |  ❌  |
| business_balance |  | No pagination | ✅ |  ❌  |
| funds | id | DefaultPaginator | ✅ |  ❌  |
| spend_programs | id | DefaultPaginator | ✅ |  ❌  |
| bills | id | DefaultPaginator | ✅ |  ❌  |
| vendors | id | DefaultPaginator | ✅ |  ❌  |
| vendor_contacts | vendor_id, id | DefaultPaginator | ✅ |  ❌  |
| vendor_agreements | id | DefaultPaginator | ✅ |  ❌  |
| receipts | id | DefaultPaginator | ✅ |  ✅  |
| merchants | id | DefaultPaginator | ✅ |  ❌  |
| purchase_orders | id | DefaultPaginator | ✅ |  ❌  |

## Limitations & troubleshooting

- The transactions stream syncs every transaction state, including declined transactions. Declined transactions have `state: DECLINED`; filter them out of spend totals. To backfill declined transactions from before version 0.1.0, refresh the `transactions` stream.
- The transactions stream includes the purchase data merchants send to Ramp, such as itemised receipt lines and flight, lodging and car rental details, in the `merchant_data` field. It is empty for transactions whose merchant sent none.
- The cards stream does not include terminated cards, because Ramp's cards list leaves them out. The stream is full refresh only, so with the **Overwrite** or **Overwrite + Deduped** sync mode a card disappears from the destination on the first sync after it is terminated. Its transactions stay in the `transactions` stream, so use a left join from `transactions.card_id` to `cards`, or read the cardholder from `transactions.card_holder`. With **Append**, the destination keeps every earlier copy of the card, and the newest copy still shows the `state` it had before termination, such as `ACTIVE`.
- The reimbursements stream syncs both directions: out-of-pocket reimbursements (BUSINESS_TO_USER) and repayments (USER_TO_BUSINESS).
- Every stream added in version 0.2.0 needs its own read scope on your Ramp app: `users:read`, `departments:read`, `locations:read`, `entities:read`, `business:read` (business and business_balance), `funds:read`, `spend_programs:read`, `bills:read`, `vendors:read` (vendors, vendor_contacts and vendor_agreements), `receipts:read`, `merchants:read` and `purchase_orders:read`. A stream whose scope is missing fails with a message naming the scope; the cards, transactions and reimbursements streams are not affected.
- The purchase_orders stream needs Ramp Plus. On other plans, deselect it.
- The users stream includes every user status, including invited, draft, inactive and suspended users. The vendors stream skips draft vendors and vendors still waiting for approval, as Ramp's API does by default. The funds stream includes terminated funds, the bills stream includes archived (deleted) bills, and the purchase_orders and vendor_agreements streams include archived records.
- The business_balance stream has no primary key: each sync emits one snapshot of the current balances.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.3.0 | 2026-10-08 | [88365](https://github.com/airbytehq/airbyte/pull/88365) | Request merchant purchase data on `transactions` and declare 10 more fields Ramp already returns |
| 0.2.1 | 2026-10-06 | [87999](https://github.com/airbytehq/airbyte/pull/87999) | Update dependencies |
| 0.2.0 | 2026-10-01 | [87610](https://github.com/airbytehq/airbyte/pull/87610) | Add 15 streams for Ramp's organisation, spend-control, accounts-payable and procurement resources |
| 0.1.0 | 2026-09-30 | [86957](https://github.com/airbytehq/airbyte/pull/86957) | Map Ramp auth and scope errors to config errors, add a rate-limit budget, filter `transactions` server-side, sync declined transactions, declare missing fields, and make `start_date` optional |
| 0.0.8 | 2026-09-29 | [87331](https://github.com/airbytehq/airbyte/pull/87331) | Update dependencies |
| 0.0.7 | 2026-09-22 | [86778](https://github.com/airbytehq/airbyte/pull/86778) | Update dependencies |
| 0.0.6 | 2026-09-15 | [86193](https://github.com/airbytehq/airbyte/pull/86193) | Update dependencies |
| 0.0.5 | 2026-09-08 | [85624](https://github.com/airbytehq/airbyte/pull/85624) | Update dependencies |
| 0.0.4 | 2026-08-18 | [84843](https://github.com/airbytehq/airbyte/pull/84843) | Add hidden configurable API base URL for sandbox testing |
| 0.0.3 | 2026-08-18 | [84721](https://github.com/airbytehq/airbyte/pull/84721) | Update dependencies |
| 0.0.2 | 2026-08-11 | [84077](https://github.com/airbytehq/airbyte/pull/84077) | Update dependencies |
| 0.0.1 | 2026-08-05 | [83706](https://github.com/airbytehq/airbyte/pull/83706) | Initial release by [@MercureTony](https://github.com/MercureTony) via Connector Builder |

</details>
