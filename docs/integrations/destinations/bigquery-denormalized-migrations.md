# BigQuery (denormalized typed struct) Migration Guide

## Upgrading to 2.0.0

`destination-bigquery-denormalized` is being retired in favor of `destination-bigquery`, and is no longer maintained. Please switch to `destination-bigquery`, which will produce similar tables and contains many improvements.  We are retiring `destination-bigquery-denormalized` because it now heavily overlaps with Destinations V2, except for being slower and less reliable. Destinations V2 is now available for BigQuery. To learn more about the feature and speed improvements of Destinations V2, please [click here](https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2)!

This connector will be retired on November first, 2023. Retired connectors will be removed from the Aribyte connector registry, and no new connections can be created with this connector. Your existing connection(s) using this connector will continue to sync, but we will no longer be offering support or updates for this connector. We will no longer be providing any updates to the `destination-bigquery-denormalized` connector.
