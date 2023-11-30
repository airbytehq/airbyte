# Sample Data (Faker) Migration Guide

## Upgrading to 5.0.0
Some columns are narrowing from `number` to `integer`. You may need to force normalization to rebuild your destination tables by manually dropping the SCD and final tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.

## Upgrading to 4.0.0

Nothing to do here - this was a test breaking change.
