# Pennylane

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_time` | `string` | Only records last updated at or after this date are synced. Use an early date to sync the full history.  |  |
| `api_key` | `string` | Pennylane Company API v2 token with read access to the synced resources.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `customer_invoices` | `id` | Cursor | ✅ | ✅ |
| `supplier_invoices` | `id` | Cursor | ✅ | ✅ |
| `customers` | `id` | Cursor | ✅ | ✅ |
| `suppliers` | `id` | Cursor | ✅ | ✅ |
| `products` | `id` | Cursor | ✅ | ✅ |
| `categories` | `id` | Cursor | ✅ | ✅ |
| `category_groups` | `id` | Cursor | ✅ | ✅ |
| `quotes` | `id` | Cursor | ✅ | ✅ |
| `ledger_accounts` | `id` | Cursor | ✅ | ✅ |
| `customer_invoice_lines` | `customer_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `customer_invoice_categories` | `customer_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `customer_invoice_matched_transactions` | `customer_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `customer_invoice_payments` | `customer_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `supplier_invoice_lines` | `supplier_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `supplier_invoice_categories` | `supplier_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `supplier_invoice_matched_transactions` | `supplier_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `supplier_invoice_payments` | `supplier_invoice_id`, `id` | Cursor | ✅ | ✅ |
| `fiscal_years` | `id` | Cursor | ✅ | ✅ |
| `ledger_entries` | `id` | Cursor | ✅ | ✅ |
| `ledger_entry_lines` | `id` | Cursor | ✅ | ✅ |
| `transactions` | `id` | Cursor | ✅ | ✅ |
| `bank_accounts` | `id` | Cursor | ✅ | ✅ |
| `billing_subscriptions` | `id` | Cursor | ✅ | ✅ |
| `purchase_requests` | `id` | Cursor | ✅ | ✅ |
| `billing_subscription_lines` | `billing_subscription_id`, `id` | Cursor | ✅ | ✅ |
| `journals` | `id` | Cursor | ✅ | ❌ |
| `trial_balance` | `fiscal_year_id`, `number` | Cursor | ✅ | ❌ |

This connector uses the [Pennylane Company API v2](https://pennylane.readme.io/). Coming from a version before 1.0.0? Read the [migration guide](pennylane-migrations.md).

### Incremental syncs

API v2 cannot filter on `updated_at`, so the connector lists every record of a stream and keeps those updated since the last sync. Nested invoice and subscription streams are read only for parents that changed, using `invoice_updated_at` or `subscription_updated_at` as their cursor. `journals` has no update timestamp and `trial_balance` is a computed snapshot, so both are always fully read.

Incremental syncs have these limits:

- A sync ignores records updated in the 5 minutes before it started or while it runs, and the next sync picks them up. This stops a change made during a long read from being skipped.
- Records deleted in Pennylane stay in the destination. Archived records are returned with `archived_at` set.
- A nested record removed from an invoice stays in the destination.
- Time-based status changes do not update `updated_at`. For example, a customer invoice can move from `upcoming` to `late` without being picked up, so compute lateness from `deadline`.
- If a change to a nested record does not update its invoice's `updated_at`, the incremental sync does not pick it up. Editing an invoice line or changing its category does update it. For matched transactions and payments, use Full Refresh if you need to be certain of catching every change.

### Sync duration

The nested streams need one API call per invoice, and the API allows 25 requests per 5 seconds. Select only the nested streams you need, as the first sync can take a long time on accounts with many invoices.

`trial_balance` returns one snapshot per fiscal year, covering the whole year.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 1.0.0 | 2026-11-06 | [91193](https://github.com/airbytehq/airbyte/pull/91193) | Migrate to Pennylane API v2, add nested invoice streams and accounting streams, and replace `plan_items` and `customer_estimates`. |
| 0.3.52 | 2026-11-03 | [90689](https://github.com/airbytehq/airbyte/pull/90689) | Update dependencies |
| 0.3.51 | 2026-10-27 | [90031](https://github.com/airbytehq/airbyte/pull/90031) | Update dependencies |
| 0.3.50 | 2026-10-20 | [89272](https://github.com/airbytehq/airbyte/pull/89272) | Update dependencies |
| 0.3.49 | 2026-10-13 | [88731](https://github.com/airbytehq/airbyte/pull/88731) | Update dependencies |
| 0.3.48 | 2026-10-06 | [87962](https://github.com/airbytehq/airbyte/pull/87962) | Update dependencies |
| 0.3.47 | 2026-09-29 | [87285](https://github.com/airbytehq/airbyte/pull/87285) | Update dependencies |
| 0.3.46 | 2026-09-22 | [86766](https://github.com/airbytehq/airbyte/pull/86766) | Update dependencies |
| 0.3.45 | 2026-09-15 | [86181](https://github.com/airbytehq/airbyte/pull/86181) | Update dependencies |
| 0.3.44 | 2026-09-08 | [85620](https://github.com/airbytehq/airbyte/pull/85620) | Update dependencies |
| 0.3.43 | 2026-08-18 | [84697](https://github.com/airbytehq/airbyte/pull/84697) | Update dependencies |
| 0.3.42 | 2026-08-11 | [84056](https://github.com/airbytehq/airbyte/pull/84056) | Update dependencies |
| 0.3.41 | 2026-08-04 | [83565](https://github.com/airbytehq/airbyte/pull/83565) | Update dependencies |
| 0.3.40 | 2026-07-28 | [83051](https://github.com/airbytehq/airbyte/pull/83051) | Update dependencies |
| 0.3.39 | 2026-07-21 | [82543](https://github.com/airbytehq/airbyte/pull/82543) | Update dependencies |
| 0.3.38 | 2026-07-14 | [81943](https://github.com/airbytehq/airbyte/pull/81943) | Update dependencies |
| 0.3.37 | 2026-06-30 | [81174](https://github.com/airbytehq/airbyte/pull/81174) | Update dependencies |
| 0.3.36 | 2026-06-23 | [80572](https://github.com/airbytehq/airbyte/pull/80572) | Update dependencies |
| 0.3.35 | 2026-06-16 | [79988](https://github.com/airbytehq/airbyte/pull/79988) | Update dependencies |
| 0.3.34 | 2026-06-09 | [79463](https://github.com/airbytehq/airbyte/pull/79463) | Update dependencies |
| 0.3.33 | 2026-06-02 | [78873](https://github.com/airbytehq/airbyte/pull/78873) | Update dependencies |
| 0.3.32 | 2026-04-28 | [77368](https://github.com/airbytehq/airbyte/pull/77368) | Update dependencies |
| 0.3.31 | 2026-04-21 | [76695](https://github.com/airbytehq/airbyte/pull/76695) | Update dependencies |
| 0.3.30 | 2026-03-31 | [75817](https://github.com/airbytehq/airbyte/pull/75817) | Update dependencies |
| 0.3.29 | 2026-03-17 | [75030](https://github.com/airbytehq/airbyte/pull/75030) | Update dependencies |
| 0.3.28 | 2026-03-10 | [74480](https://github.com/airbytehq/airbyte/pull/74480) | Update dependencies |
| 0.3.27 | 2026-02-24 | [73839](https://github.com/airbytehq/airbyte/pull/73839) | Update dependencies |
| 0.3.26 | 2026-02-17 | [73193](https://github.com/airbytehq/airbyte/pull/73193) | Update dependencies |
| 0.3.25 | 2026-02-03 | [72664](https://github.com/airbytehq/airbyte/pull/72664) | Update dependencies |
| 0.3.24 | 2026-01-20 | [72189](https://github.com/airbytehq/airbyte/pull/72189) | Update dependencies |
| 0.3.23 | 2026-01-14 | [71545](https://github.com/airbytehq/airbyte/pull/71545) | Update dependencies |
| 0.3.22 | 2025-12-18 | [70487](https://github.com/airbytehq/airbyte/pull/70487) | Update dependencies |
| 0.3.21 | 2025-11-25 | [69972](https://github.com/airbytehq/airbyte/pull/69972) | Update dependencies |
| 0.3.20 | 2025-11-18 | [69617](https://github.com/airbytehq/airbyte/pull/69617) | Update dependencies |
| 0.3.19 | 2025-10-29 | [68995](https://github.com/airbytehq/airbyte/pull/68995) | Update dependencies |
| 0.3.18 | 2025-10-21 | [68262](https://github.com/airbytehq/airbyte/pull/68262) | Update dependencies |
| 0.3.17 | 2025-10-14 | [67795](https://github.com/airbytehq/airbyte/pull/67795) | Update dependencies |
| 0.3.16 | 2025-10-07 | [67346](https://github.com/airbytehq/airbyte/pull/67346) | Update dependencies |
| 0.3.15 | 2025-10-01 | [66965](https://github.com/airbytehq/airbyte/pull/66965) | Update dependencies |
| 0.3.14 | 2025-09-23 | [66425](https://github.com/airbytehq/airbyte/pull/66425) | Update dependencies |
| 0.3.13 | 2025-09-10 | [65753](https://github.com/airbytehq/airbyte/pull/65753) | Update dependencies |
| 0.3.12 | 2025-08-23 | [65220](https://github.com/airbytehq/airbyte/pull/65220) | Update dependencies |
| 0.3.11 | 2025-08-09 | [64769](https://github.com/airbytehq/airbyte/pull/64769) | Update dependencies |
| 0.3.10 | 2025-08-02 | [64225](https://github.com/airbytehq/airbyte/pull/64225) | Update dependencies |
| 0.3.9 | 2025-07-26 | [63817](https://github.com/airbytehq/airbyte/pull/63817) | Update dependencies |
| 0.3.8 | 2025-07-19 | [63404](https://github.com/airbytehq/airbyte/pull/63404) | Update dependencies |
| 0.3.7 | 2025-07-12 | [63196](https://github.com/airbytehq/airbyte/pull/63196) | Update dependencies |
| 0.3.6 | 2025-07-05 | [62622](https://github.com/airbytehq/airbyte/pull/62622) | Update dependencies |
| 0.3.5 | 2025-06-28 | [62387](https://github.com/airbytehq/airbyte/pull/62387) | Update dependencies |
| 0.3.4 | 2025-06-21 | [61925](https://github.com/airbytehq/airbyte/pull/61925) | Update dependencies |
| 0.3.3 | 2025-06-14 | [61062](https://github.com/airbytehq/airbyte/pull/61062) | Update dependencies |
| 0.3.2 | 2025-05-24 | [60575](https://github.com/airbytehq/airbyte/pull/60575) | Update dependencies |
| 0.3.1 | 2025-05-10 | [60071](https://github.com/airbytehq/airbyte/pull/60071) | Update dependencies |
| 0.3.0 | 2025-05-09 | [59679](https://github.com/airbytehq/airbyte/pull/59679) | Add  stream `customer_estimates` stream |
| 0.2.9 | 2025-05-03 | [59078](https://github.com/airbytehq/airbyte/pull/59078) | Update dependencies |
| 0.2.8 | 2025-04-19 | [57882](https://github.com/airbytehq/airbyte/pull/57882) | Update dependencies |
| 0.2.7 | 2025-04-05 | [57347](https://github.com/airbytehq/airbyte/pull/57347) | Update dependencies |
| 0.2.6 | 2025-03-29 | [56788](https://github.com/airbytehq/airbyte/pull/56788) | Update dependencies |
| 0.2.5 | 2025-03-22 | [56221](https://github.com/airbytehq/airbyte/pull/56221) | Update dependencies |
| 0.2.4 | 2025-03-08 | [55556](https://github.com/airbytehq/airbyte/pull/55556) | Update dependencies |
| 0.2.3 | 2025-03-01 | [55024](https://github.com/airbytehq/airbyte/pull/55024) | Update dependencies |
| 0.2.2 | 2025-02-23 | [54601](https://github.com/airbytehq/airbyte/pull/54601) | Update dependencies |
| 0.2.1 | 2025-02-15 | [50686](https://github.com/airbytehq/airbyte/pull/50686) | Update dependencies |
| 0.2.0 | 2025-01-29 | [52596](https://github.com/airbytehq/airbyte/pull/52596) | Fixes for category_groups and plan_items |
| 0.1.1 | 2024-12-21 | [50294](https://github.com/airbytehq/airbyte/pull/50294) | Update dependencies |
| 0.1.0 | 2024-12-10 | [48892](https://github.com/airbytehq/airbyte/pull/48892) | Add missing fields to `customer_invoices` stream |
| 0.0.6 | 2024-12-14 | [49659](https://github.com/airbytehq/airbyte/pull/49659) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49322](https://github.com/airbytehq/airbyte/pull/49322) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49053](https://github.com/airbytehq/airbyte/pull/49053) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47902](https://github.com/airbytehq/airbyte/pull/47902) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47536](https://github.com/airbytehq/airbyte/pull/47536) | Update dependencies |
| 0.0.1 | 2024-08-21 | | Initial release by natikgadzhi via Connector Builder |

</details>
