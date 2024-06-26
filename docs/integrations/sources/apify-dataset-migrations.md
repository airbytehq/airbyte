# Apify Dataset Migration Guide

## Upgrading to 2.0.0

Major update: The old broken Item Collection stream has been removed and replaced with a new Item Collection (WCC) stream specific for the datasets produced by [Website Content Crawler](https://apify.com/apify/website-content-crawler) Actor. In a follow-up release 2.1.0, a generic item collection stream will be added to support all other datasets.

After upgrading, users should:

- Reconfigure dataset id and API key
- Reset all streams

## Upgrading to 1.0.0

A major update fixing the data ingestion to retrieve properly data from Apify.
Please update your connector configuration setup.
