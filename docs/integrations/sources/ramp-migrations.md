# Ramp Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
The upgrade asks you to clear the `cards`, `transactions` and `reimbursements` streams. Clearing deletes their data in your destination, and the next sync reads back only the current version of each record from your start date onward. If you sync these streams with an **Append** mode, the earlier copies of a record that Append kept, and any records older than your start date, don't come back. Back up these tables before you clear them if you need that history.
:::

Version 1.0.0 declares the date and timestamp fields of the `cards`, `transactions` and `reimbursements` streams with their real types. Ramp returns these values in ISO 8601 format, but earlier versions declared them as plain strings, so destinations stored them as text and you had to cast them before filtering or joining by date. Every ISO 8601 date field of the other 15 streams was already typed when the stream was added.

### What changed

These 13 fields change type. Destinations that type their columns change the matching columns from text to the new type.

| Stream | Field | New type |
| --- | --- | --- |
| `cards` | `created_at` | Timestamp with time zone |
| `transactions` | `accounting_date` | Timestamp with time zone |
| `transactions` | `settlement_date` | Timestamp with time zone |
| `transactions` | `synced_at` | Timestamp with time zone |
| `transactions` | `updated_at` | Timestamp with time zone |
| `transactions` | `user_transaction_time` | Timestamp with time zone |
| `reimbursements` | `accounting_date` | Timestamp with time zone |
| `reimbursements` | `approved_at` | Timestamp with time zone |
| `reimbursements` | `created_at` | Timestamp with time zone |
| `reimbursements` | `submitted_at` | Timestamp with time zone |
| `reimbursements` | `synced_at` | Timestamp with time zone |
| `reimbursements` | `updated_at` | Timestamp with time zone |
| `reimbursements` | `transaction_date` | Date |

The values themselves don't change, and no field is added or removed. `transactions.accounting_date` and `settlement_date` are full timestamps despite their names, because that is what Ramp returns.

Three date-like fields stay strings because Ramp doesn't return them in ISO 8601 format: `cards.expiration` (`MMYY`, for example `0430`) and `business_balance.next_billing_date` and `prev_billing_date` (`MM/DD/YYYY`).

### Who is affected

Connections that sync at least one of the `cards`, `transactions` and `reimbursements` streams. Connections that sync none of them aren't affected.

### Upgrade steps

1. If you sync these streams with an **Append** mode and need the history it kept, back up the `cards`, `transactions` and `reimbursements` tables.
2. Upgrade the connector to 1.0.0.
3. Before the connection's next sync, refresh the source schema, and clear the `cards`, `transactions` and `reimbursements` streams. The [connector upgrade guide](#connector-upgrade-guide) below has the steps.
4. Sync the connection. The `transactions` and `reimbursements` streams re-read every record updated since your start date, or since 2019-01-01 if you didn't set one.

### Update downstream queries

Update the SQL, dbt models, dashboards and exports that read the 13 fields above:

- Remove the casts and date-parsing functions you added to turn these columns into dates, such as `CAST(updated_at AS TIMESTAMP)`, `PARSE_TIMESTAMP` or `TO_TIMESTAMP`.
- Replace string functions on these columns, such as `LIKE '2026-%'` or `SUBSTRING(transaction_date, 1, 7)`, with date and timestamp functions.

## Connector upgrade guide

<MigrationGuide />
