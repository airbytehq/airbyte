# Airtable Migration Guide

## Upgrading to 4.0.0

Columns with Formulas are narrowing from `array` to `string` or `number`. You may need to refresh the connection schema (with the reset), and run a sync.
