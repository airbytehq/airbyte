# Orb Migration Guide

## Upgrading to 2.0.0

This version migrates the Orb connector to our low-code framework for greater maintainability.

As part of this release, we've also updated data types across streams to match the correct return types from the upstream API. You will need to run a reset on connections using this connector after upgrading to continue syncing.
The data type of the `credit_block_per_unit_cost_basis` field (primary key) in the `credits_ledger_entries` stream has been changed from `string` to `number`
