# Track PMS Migration Guide

## Upgrading to 3.0.0

The redundant `_embedded` field has been removed from the following streams:
* `accounting_accounts`
* `accounting_bills`
* `accounting_charges`
* `accounting_deposits`
* `accounting_transactions`
This redundant information was also prone to contain unnecessary sensitive information, like SSNs.

Accounting_accounts added a query parameter `includeRestricted=1` to pull more comprehensive account information.

The duplicated `owners_statements_transactions_pii_redacted` was dropped - it had the same configuration as `owners_statements_transactions`.

The duplicated `folios_master_rules` was dropped - it had the same configuration as `folio_rules`.

The `owners_statements_transactions._embedded` column was tweaked to keep only `paymentType` and `reservation`; other known fields obtainable by joining to other streams.

Please update and resynchronize all data from the above streams from your connections.

## Upgrading to 2.0.0

Streams have been renamed to follow the established convention and have been normalized. Please update and resynchronize all data from your connections.

This change renamed the following streams:
- `folio_logs` -> `folios_logs`

## Upgrading to 1.0.0

Streams have been renamed to follow the established convention and have been normalized. Please update and resynchronize all data from your connections.

