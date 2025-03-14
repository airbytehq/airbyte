# Typesense

## Overview

The Airbyte Typesense destination allows you to sync data to Airbyte.Typesense is a modern, privacy-friendly, open source search engine built from the ground up using cutting-edge search algorithms, that take advantage of the latest advances in hardware capabilities.

### Sync overview

Using overwrite sync, the [auto schema detection](https://typesense.org/docs/0.23.1/api/collections.html#with-auto-schema-detection) is used and all the fields in a document are automatically indexed for searching and filtering

With append mode, you have to create the collection first and can use [pre-defined schema](https://typesense.org/docs/0.23.1/api/collections.html#with-pre-defined-schema) that gives you fine-grained control over your document fields.

#### Output schema

Each stream will be output into its own collection in Typesense. If an id column is not provided, it will be generated.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | No                   |       |

## Getting started

### Requirements

To use the Typesense destination, you'll need an existing Typesense instance. You can learn about how to create one in the [Typesense docs](https://typesense.org/docs/guide/install-typesense.html).

### Setup guide

The setup only requires two fields. First is the `host` which is the address at which Typesense can be reached. The second piece of information is the API key.

### Typesense with High Availability

To connect a Typesense with HA, you can type multiple hosts on the host field using a comma separator.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| 0.1.43 | 2025-03-08 | [55373](https://github.com/airbytehq/airbyte/pull/55373) | Update dependencies |
| 0.1.42 | 2025-03-01 | [54910](https://github.com/airbytehq/airbyte/pull/54910) | Update dependencies |
| 0.1.41 | 2025-02-22 | [53929](https://github.com/airbytehq/airbyte/pull/53929) | Update dependencies |
| 0.1.40 | 2025-02-08 | [53387](https://github.com/airbytehq/airbyte/pull/53387) | Update dependencies |
| 0.1.39 | 2025-02-04 | [49984](https://github.com/airbytehq/airbyte/pull/49984) | Typo default port |
| 0.1.38 | 2025-02-04 | [53131](https://github.com/airbytehq/airbyte/pull/53131) | Document id is overwritten by writer |
| 0.1.37 | 2025-02-01 | [52945](https://github.com/airbytehq/airbyte/pull/52945) | Update dependencies |
| 0.1.36 | 2025-01-25 | [52170](https://github.com/airbytehq/airbyte/pull/52170) | Update dependencies |
| 0.1.35 | 2025-01-18 | [51734](https://github.com/airbytehq/airbyte/pull/51734) | Update dependencies |
| 0.1.34 | 2025-01-11 | [51253](https://github.com/airbytehq/airbyte/pull/51253) | Update dependencies |
| 0.1.33 | 2024-12-28 | [50501](https://github.com/airbytehq/airbyte/pull/50501) | Update dependencies |
| 0.1.32 | 2024-12-21 | [50175](https://github.com/airbytehq/airbyte/pull/50175) | Update dependencies |
| 0.1.31 | 2024-12-14 | [49282](https://github.com/airbytehq/airbyte/pull/49282) | Update dependencies |
| 0.1.30 | 2024-11-25 | [48676](https://github.com/airbytehq/airbyte/pull/48676) | Update dependencies |
| 0.1.29 | 2024-11-04 | [47077](https://github.com/airbytehq/airbyte/pull/47077) | Update dependencies |
| 0.1.28 | 2024-10-12 | [46810](https://github.com/airbytehq/airbyte/pull/46810) | Update dependencies |
| 0.1.27 | 2024-10-05 | [46426](https://github.com/airbytehq/airbyte/pull/46426) | Update dependencies |
| 0.1.26 | 2024-09-28 | [46119](https://github.com/airbytehq/airbyte/pull/46119) | Update dependencies |
| 0.1.25 | 2024-09-21 | [45768](https://github.com/airbytehq/airbyte/pull/45768) | Update dependencies |
| 0.1.24 | 2024-09-14 | [45491](https://github.com/airbytehq/airbyte/pull/45491) | Update dependencies |
| 0.1.23 | 2024-09-07 | [45265](https://github.com/airbytehq/airbyte/pull/45265) | Update dependencies |
| 0.1.22 | 2024-08-31 | [45057](https://github.com/airbytehq/airbyte/pull/45057) | Update dependencies |
| 0.1.21 | 2024-08-24 | [44683](https://github.com/airbytehq/airbyte/pull/44683) | Update dependencies |
| 0.1.20 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.19 | 2024-08-17 | [44339](https://github.com/airbytehq/airbyte/pull/44339) | Update dependencies |
| 0.1.18 | 2024-08-10 | [43489](https://github.com/airbytehq/airbyte/pull/43489) | Update dependencies |
| 0.1.17 | 2024-08-01 | [42868](https://github.com/airbytehq/airbyte/pull/42868) | Allows you to specify multiple hosts, separated by commas, to connect to Typesense with HA. |
| 0.1.16 | 2024-08-03 | [43282](https://github.com/airbytehq/airbyte/pull/43282) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42606](https://github.com/airbytehq/airbyte/pull/42606) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42146](https://github.com/airbytehq/airbyte/pull/42146) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41881](https://github.com/airbytehq/airbyte/pull/41881) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41361](https://github.com/airbytehq/airbyte/pull/41361) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41220](https://github.com/airbytehq/airbyte/pull/41220) | Update dependencies |
| 0.1.10 | 2024-07-06 | [40918](https://github.com/airbytehq/airbyte/pull/40918) | Update dependencies |
| 0.1.9 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.8 | 2024-06-25 | [40487](https://github.com/airbytehq/airbyte/pull/40487) | Update dependencies |
| 0.1.7 | 2024-06-22 | [40154](https://github.com/airbytehq/airbyte/pull/40154) | Update dependencies |
| 0.1.6 | 2024-06-04 | [39050](https://github.com/airbytehq/airbyte/pull/39050) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.5 | 2024-05-20 | [38428](https://github.com/airbytehq/airbyte/pull/38428) | [autopull] base image + poetry + up_to_date |
| 0.1.4 | 2024-03-25 | [36460](https://github.com/airbytehq/airbyte/pull/36460) | Added path config option |
| 0.1.3 | 2024-01-17 | [34336](https://github.com/airbytehq/airbyte/pull/34336) | Fix check() arguments error |
| 0.1.2 | 2023-08-25 | [29817](https://github.com/airbytehq/airbyte/pull/29817) | Fix writing multiple streams |
| 0.1.1 | 2023-08-24 | [29555](https://github.com/airbytehq/airbyte/pull/29555) | Increasing connection timeout |
| 0.1.0 | 2022-10-28 | [18349](https://github.com/airbytehq/airbyte/pull/18349) | New Typesense destination |

</details>
