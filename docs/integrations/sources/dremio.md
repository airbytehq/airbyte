# Dremio

## Overview

The Dremio source supports Full Refresh sync. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Catalogs](https://docs.dremio.com/software/rest-api/catalog/get-catalog/) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| SSL connection            | Yes        |
| Namespaces                | No         |

## Getting started

### Requirements

- API Key
- Base URL

### Setup guide

Connector needs a self-hosted instance of Dremio, this way you can access the Dremio REST API on which this source is based. Please refer to [Dremio Deployment Models](https://docs.dremio.com/software/deployment/deployment-models/) document, or take a look at [Dremio OSS](https://github.com/dremio/dremio-oss) for reference.

Please read [How to get your APIs credentials](https://docs.dremio.com/software/rest-api/#authenticationn).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject            |
| :------ | :--------- | :------------------------------------------------------- | :----------------- |
| 0.2.13 | 2025-02-15 | [53777](https://github.com/airbytehq/airbyte/pull/53777) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53335](https://github.com/airbytehq/airbyte/pull/53335) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52837](https://github.com/airbytehq/airbyte/pull/52837) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52330](https://github.com/airbytehq/airbyte/pull/52330) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51690](https://github.com/airbytehq/airbyte/pull/51690) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51124](https://github.com/airbytehq/airbyte/pull/51124) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50558](https://github.com/airbytehq/airbyte/pull/50558) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50029](https://github.com/airbytehq/airbyte/pull/50029) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49529](https://github.com/airbytehq/airbyte/pull/49529) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49194](https://github.com/airbytehq/airbyte/pull/49194) | Update dependencies |
| 0.2.3 | 2024-12-11 | [48904](https://github.com/airbytehq/airbyte/pull/48904) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-10-29 | [47886](https://github.com/airbytehq/airbyte/pull/47886) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47633](https://github.com/airbytehq/airbyte/pull/47633) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44415](https://github.com/airbytehq/airbyte/pull/44415) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-17 | [44311](https://github.com/airbytehq/airbyte/pull/44311) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43785](https://github.com/airbytehq/airbyte/pull/43785) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43608](https://github.com/airbytehq/airbyte/pull/43608) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43201](https://github.com/airbytehq/airbyte/pull/43201) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42670](https://github.com/airbytehq/airbyte/pull/42670) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42186](https://github.com/airbytehq/airbyte/pull/42186) | Update dependencies |
| 0.1.9 | 2024-07-17 | [38692](https://github.com/airbytehq/airbyte/pull/38692) | Make compatible with builder |
| 0.1.8 | 2024-07-13 | [41812](https://github.com/airbytehq/airbyte/pull/41812) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41578](https://github.com/airbytehq/airbyte/pull/41578) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41127](https://github.com/airbytehq/airbyte/pull/41127) | Update dependencies |
| 0.1.5 | 2024-07-06 | [41008](https://github.com/airbytehq/airbyte/pull/41008) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40471](https://github.com/airbytehq/airbyte/pull/40471) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40045](https://github.com/airbytehq/airbyte/pull/40045) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39235](https://github.com/airbytehq/airbyte/pull/39235) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38497](https://github.com/airbytehq/airbyte/pull/38497) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-12-01 | [19912](https://github.com/airbytehq/airbyte/pull/19912) | New Source: Dremio |

</details>
