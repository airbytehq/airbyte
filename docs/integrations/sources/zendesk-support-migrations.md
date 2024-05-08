# Zendesk Support Migration Guide

## Upgrading to 2.0.0

Stream `Deleted Tickets` is removed. You may need to refresh the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.

## Upgrading to 1.0.0

`cursor_field` for `Tickets` stream is changed to `generated_timestamp`.
For a smooth migration, data reset and schema refresh are needed.
