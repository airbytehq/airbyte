# MySQL Migration Guide

## Upgrading to 4.0.0

This release is a complete rewrite of source mysql and was built with backward compability. No user action is necessary. when updating to 4.0.0.

## Upgrading to 3.0.0

CDC syncs now has default cursor field called `_ab_cdc_cursor`. You will need to force normalization to rebuild your destination tables by manually dropping the SCD tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.
