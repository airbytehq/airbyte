# Orb Migration Guide

## Upgrading to 2.0.0

The `credit_block_per_unit_cost_basis` field in the `credits_ledger_entries` stream was modified from `string` datatype to `number` datatype. You may need to refresh the schema and run a sync.
