# Ramp
Syncs cards, transactions and reimbursements, plus Ramp&#39;s organisation, spend-control, accounts-payable and procurement data, from Ramp&#39;s developer API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `credentials` | `object` | Authentication. Choose **OAuth** or **Client Credentials**. |  |
| `credentials.client_id` | `string` | Client Credentials only: client ID of your Ramp developer app (Ramp > Company > Developer). The app needs the Client Credentials grant and the read scope of every stream you sync. |  |
| `credentials.client_secret` | `string` | Client Credentials only: client secret of the same Ramp developer app. |  |
| `start_date` | `string` | Start Date. Earliest updated_at to pull on the initial sync of the transactions and reimbursements streams, and earliest created_at for the receipts stream. Format ISO 8601 with Z suffix (e.g. 2024-01-01T00:00:00Z). Ignored on subsequent incremental syncs. | 2019-01-01T00:00:00Z |

### Authentication

- **OAuth.** Click **Authenticate your Ramp account** and approve access in Ramp. Only a Ramp Admin or Business Owner can approve it; other users see "Business not authorized to use this application". The consent grants the read scope of every stream. If a sync later fails because Ramp rejected the authorization, re-authenticate the source.
- **Client Credentials.** Create a developer app in Ramp > Company > Developer with the Client Credentials grant and the read scopes of the streams you sync, then enter its client ID and client secret.

Sources created before version 0.3.0 are moved to the Client Credentials option automatically and keep working without changes.

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
- The cards stream does not include terminated cards, because Ramp's cards list leaves them out. The stream is full refresh only, so with the **Overwrite** or **Overwrite + Deduped** sync mode a card disappears from the destination on the first sync after it is terminated. Its transactions stay in the `transactions` stream, so use a left join from `transactions.card_id` to `cards`, or read the cardholder from `transactions.card_holder`. With **Append**, the destination keeps every earlier copy of the card, and the newest copy still shows the `state` it had before termination, such as `ACTIVE`.
- The reimbursements stream syncs both directions: out-of-pocket reimbursements (BUSINESS_TO_USER) and repayments (USER_TO_BUSINESS).
- With Client Credentials, every stream added in version 0.2.0 needs its own read scope on your Ramp app: `users:read`, `departments:read`, `locations:read`, `entities:read`, `business:read` (business and business_balance), `funds:read`, `spend_programs:read`, `bills:read`, `vendors:read` (vendors, vendor_contacts and vendor_agreements), `receipts:read`, `merchants:read` and `purchase_orders:read`. A stream whose scope is missing fails with a message naming the scope; the cards, transactions and reimbursements streams are not affected.
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
| 0.3.0 | 2026-10-06 | [88128](https://github.com/airbytehq/airbyte/pull/88128) | Add OAuth authentication; existing client-credentials configs are migrated automatically |
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
