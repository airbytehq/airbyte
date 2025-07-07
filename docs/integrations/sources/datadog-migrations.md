# Datadog Migration Guide

## Upgrading to 2.0.0

On December 13, 2024, Datadog is removing support for the `is_read_only` attribute in the Dashboards API’s. Hence, the `is_read_only` attribute will no longer be available in the dashboards stream response. Upgrade and resync to reset the schema and update the records.

## Upgrading to 1.0.0

Starting 1.0, Datadog source will apply start and end dates to sync data incrementally. When upgrading, take a minute to set start and end date config options.

