# Apify dataset

## Overview


The Apify dataset connect supports full refresh sync only.

It can sync data from a single [Apify Dataset](https://docs.apify.com/storage/dataset) by its ID.

### Output schema

Since the dataset items do not have strongly typed schema, they are synced as objects, without any assumption on their content.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |

### Performance considerations

The Apify dataset connector uses [Apify Python Client](https://docs.apify.com/apify-client-python) under the hood and should handle any API limitations under normal usage.

## Getting started

### Requirements

* Dataset Id

### Changelog
| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-07-29 | [PR#5069](https://github.com/airbytehq/airbyte/pull/5069) | Initial version of the connector |