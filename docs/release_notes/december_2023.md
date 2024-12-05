# December 2023

## airbyte v0.50.36 to v0.50.40

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

## ✨ Highlights

Airbyte introduced a new schemaless mode for our MongoDB source connector to improve our ability to sync data from collections with varying fields for each document. This enhancement not only streamlines connector configuration, but also ensures reliable data propagation, even when upstream teams modify the fields uploaded to new MongoDB documents in your collection.

## Connector Improvements

In addition to our schemaless mode for MongoDB, we have also:

- Enhanced our [Bing Ads](https://github.com/airbytehq/airbyte/pull/33095) source by allowing for account-specific filtering and improved error handling.
- Enabled per-stream state for [MS SQL](https://github.com/airbytehq/airbyte/pull/33018) source to increase resiliency to stream changes.
- Published a new [OneDrive](https://github.com/airbytehq/airbyte/pull/32655) source connector to support additional unstructured data in files.
- Added streams for our [Hubspot](https://github.com/airbytehq/airbyte/pull/33266) source to add `property_history` for Companies and Deals. We also added incremental syncing for all property history streams for increased sync reliability.
- Improved our [Klaviyo](https://github.com/airbytehq/airbyte/pull/33099) source connector to account for rate-limiting and gracefully handle stream-specific errors to continue syncing other streams
