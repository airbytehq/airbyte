# Apify Dataset Migration Guide

## Upgrading to 2.0.0

Major update: The old broken Item Collection stream has been removed and replaced with a new Item Collection (WCC) stream specific for the datasets produced by [Website Content Crawler](https://apify.com/apify/website-content-crawler) Actor. Please update your connector configuration setup. Note: The schema of the Apify Dataset is at least Actor-specific, so we cannot have a general Stream with a static schema for getting data from a Dataset.

## Upgrading to 1.0.0

A major update fixing the data ingestion to retrieve properly data from Apify.
Please update your connector configuration setup.