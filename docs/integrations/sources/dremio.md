# Dremio

## Overview

The Dremio source supports Full Refresh sync. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

- [Catalogs](https://docs.dremio.com/software/rest-api/catalog/get-catalog/) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| SSL connection | Yes |
| Namespaces | No |

## Getting started

### Requirements

* API Key
* Base URL

### Setup guide

Please read [How to get your APIs credentials](https://docs.dremio.com/software/rest-api/overview/#authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-12-01 | [19912](https://github.com/airbytehq/airbyte/pull/19912) | New Source: Dremio |

