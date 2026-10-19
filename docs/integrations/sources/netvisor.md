# Netvisor

The Netvisor source reads your company's accounting data for reporting and analysis. It supports Netvisor's test and production environments.

## Prerequisites

- A Netvisor company with Web Service Interface access enabled.
- Customer API identifiers for a user who can access that company.
- A partner ID and partner key issued by Netvisor for the selected environment. Contact your integration provider or [Netvisor's integration team](https://netvisor.fi/ohjelmistokumppanuus/) to arrange partner access.
- Permission to read the API resources listed below.

## Setup guide

### Set up Netvisor

1. Create a customer API ID and key using Netvisor's [API identifier instructions](https://support.netvisor.fi/en/articles/766837-api-identifiers).
2. Enable the integration for the company in Netvisor's API access settings. For a custom integration, use the partner search key supplied by Netvisor to locate it. See [Rights of API resources](https://support.netvisor.fi/en/articles/766836-rights-of-api-resources).
3. Enable all seven API resources below; the connection check requires access to each.

| API resource              | Streams                                  |
| ------------------------- | ---------------------------------------- |
| `accountbalance.nv`       | `account_balances`                       |
| `accountingledger.nv`     | `accounting_ledger`                      |
| `accountingperiodlist.nv` | `accounting_periods`, `accounting_locks` |
| `accountlist.nv`          | `accounts`, `default_accounts`           |
| `getbankaccounts.nv`      | `bank_accounts`                          |
| `dimensionlist.nv`        | `dimensions`                             |
| `vouchertypelist.nv`      | `voucher_types`, `default_voucher_types` |

### Set up Airbyte

1. Create a Netvisor source and choose **Environment**: `test` or `production`.
2. Enter the **Customer API ID**, **Customer API key**, **Partner ID**, and **Partner key** for that environment.
3. Enter the company's Finnish business ID as **Company business ID**, including its hyphen.
4. Set **Sync history start date** in `YYYY-MM-DD` format. Choose a date on or before the earliest history you need. Future dates are not accepted.
5. Optionally change **Days per request** (1–31, default 30) and **Response language** (`FI`, `SE`, or `EN`; default `EN`).
6. Test the connection and select the streams and sync modes for your connection.

## Supported streams and sync modes

All streams support Full Refresh. Only `accounting_ledger` supports Incremental. Destination capabilities determine which append, overwrite, and deduplication options are available.

| Stream                  | One record represents                                                               | Primary key                         |
| ----------------------- | ----------------------------------------------------------------------------------- | ----------------------------------- |
| `account_balances`      | One account's daily debit, credit, and balance totals                               | `company_id`, `Netvisorkey`, `Date` |
| `accounting_ledger`     | One accounting voucher, with its voucher lines and their dimensions and allocations | `company_id`, `NetvisorKey`         |
| `accounting_locks`      | The company's accounting, VAT, and purchase lock dates                              | `company_id`                        |
| `accounting_periods`    | One accounting period                                                               | `company_id`, `NetvisorKey`         |
| `accounts`              | One chart-of-accounts entry                                                         | `company_id`, `NetvisorKey`         |
| `bank_accounts`         | One company bank account                                                            | `company_id`, `IBAN`                |
| `default_accounts`      | The company's default account settings                                              | `company_id`                        |
| `default_voucher_types` | The company's default voucher type settings                                         | `company_id`                        |
| `dimensions`            | One dimension with its nested dimension details                                     | `company_id`, `Netvisorkey`         |
| `voucher_types`         | One voucher type                                                                    | `company_id`, `NetvisorKey`         |

A voucher is an accounting entry containing a header and zero or more posting lines. The ledger keeps these lines in the `VoucherLine` array so each voucher remains a complete record. Dimension details and transaction allocations also remain nested.

### Accounting ledger

The ledger fetches vouchers by their last modification date. **Sync history start date is a modification-date boundary, not a voucher-date filter.** Choose an early enough date for the initial sync. See [Netvisor's ledger API documentation](https://support.netvisor.fi/en/articles/766887-get-accounting-data-accountingledger-nv).

Incremental syncs resume from saved state with a two-day lookback. Requests also overlap the window boundaries by one day to accommodate the API's date filtering. The connector exposes `_netvisor_sync_window_end` as its sync cursor; it is not a voucher's modification timestamp.

Overlapping requests can emit a voucher more than once. Use Incremental Append + Deduped where supported to maintain the latest version of each voucher. Append mode retains the emitted versions.

The ledger includes valid, invalidated, and deleted vouchers. These are emitted as records with the API's `status` value; the connector does not physically delete destination rows. Use the latest voucher and line statuses when interpreting postings.

### Account balances and reference data

`account_balances` fetches daily values from **Sync history start date** through today in UTC on every sync. Dates are grouped into requests using **Days per request**. Each request returns daily balances. Every sync re-reads historical values to reflect corrections. Interpret totals with the account's `IsCumulative` flag.

The remaining streams retrieve complete snapshots and ignore the start date. Use Full Refresh Overwrite where supported if you want only the current snapshot. Empty lists are valid when a company has no bank accounts or dimensions. Unset lock dates can be absent from an `accounting_locks` record.

## Data representation

Field names retain Netvisor's casing, including API differences such as `NetvisorKey` and `Netvisorkey`. XML attributes become ordinary fields, and text accompanying XML attributes uses a `value` field. The connector adds `company_id` to identify the source company.

Identifiers remain strings. Documented flags are converted to booleans, and normalized date fields use `YYYY-MM-DD`. Monetary values retain Netvisor's exact decimal representation as strings; convert them to decimal types with the appropriate decimal separator when analyzing them.

## Limitations and troubleshooting

- Requests run sequentially. Avoid overlapping syncs against the same company. Reduce **Days per request** if responses become too large; smaller windows increase the number of requests.
- Authentication failures usually require checking the environment, both credential pairs, the company business ID, and API resource permissions.
- API credential values must contain only ASCII characters.
- Netvisor may reject an automatic retry with `REQUEST_NOT_UNIQUE` because the retry reuses the request's authentication headers. Restart the sync if this occurs.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject          |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.0.1   | 2026-10-19 | [89075](https://github.com/airbytehq/airbyte/pull/89075) | Initial release. |

</details>
