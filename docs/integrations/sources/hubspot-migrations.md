# Hubspot Migration Guide

## Upgrading to 2.0.0

A major update of most streams to change their schemas in order to unnest some top-level properties by one level. This allows the data to be represented as a table column, not to be nested in a JSON-like object, so it's easy to query it in the new Destinations V2 regarding it will no longer support the normalization, so nested data will no longer be represented as a separate table.
A schema refresh and data reset is required for the connector to use the new version.