# Typesense

## Overview

The Airbyte Typesense destination allows you to sync data to Airbyte.Typesense is a modern, privacy-friendly, open source search engine built from the ground up using cutting-edge search algorithms, that take advantage of the latest advances in hardware capabilities.

### Sync overview

Using overwrite sync, the [auto schema detection](https://typesense.org/docs/0.23.1/api/collections.html#with-auto-schema-detection) is used and all the fields in a document are automatically indexed for searching and filtering

With append mode, you have to create the collection first and can use [pre-defined schema](https://typesense.org/docs/0.23.1/api/collections.html#with-pre-defined-schema) that gives you fine-grained control over your document fields.

#### Output schema

Each stream will be output into its own collection in Typesense. If an id column is not provided, it will be generated.

#### Features

| Feature                       | Supported?\(Yes/No\) | Notes                                                                                        |
| :---------------------------- | :------------------- | :------------------------------------------------------------------------------------------- |
| Full Refresh Sync             | Yes                  |                                                                                              |
| Incremental - Append Sync     | Yes                  |                                                                                              |
| Incremental - Deduped History | No                   | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces                    | No                   |                                                                                              |

## Getting started

### Requirements

To use the Typesense destination, you'll need an existing Typesense instance. You can learn about how to create one in the [Typesense docs](https://typesense.org/docs/guide/install-typesense.html).

### Setup guide

The setup only requires two fields. First is the `host` which is the address at which Typesense can be reached. The second piece of information is the API key.

## Changelog

| Version | Date | Pull Request | Subject |
| 0.1.0 | 2022-10-28 | [18349](https://github.com/airbytehq/airbyte/pull/18349) | New Typesense destination |
