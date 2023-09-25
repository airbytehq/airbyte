# Timeplus

This page guides you through the process of setting up the [Timeplus](https://timeplus.com) destination connector.

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Overwrite | Yes |  |
| Incremental - Append Sync | Yes |  |


#### Output Schema

Each stream will be output into its own stream in Timeplus, with corresponding schema/columns.
## Getting Started (Airbyte Cloud)
Coming soon...

## Getting Started (Airbyte Open-Source)
You can follow the [Quickstart with Timeplus Ingestion API](https://docs.timeplus.com/quickstart-ingest-api) to createa a workspace and API key.

### Setup the Timeplus Destination in Airbyte

You should now have all the requirements needed to configure Timeplus as a destination in the UI. You'll need the following information to configure the Timeplus destination:

* **Endpoint** example https://us.timeplus.cloud/randomId123
* **API key**

## Compatibility


## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2023-06-14 | [21226](https://github.com/airbytehq/airbyte/pull/21226) | Destination Timeplus                            |

