# US Census API

## Overview

This connector syncs data from the [US Census API](https://www.census.gov/data/developers/guidance/api-user-guide.Example_API_Queries.html)

<!-- env:oss -->

### Output schema

This source always outputs a single stream, `us_census_stream`. The output of the stream depends on the configuration of the connector.

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

<!-- /env:oss -->

## Getting started

### Requirements

- US Census API key
- US Census dataset path & query parameters

### Setup guide

Visit the [US Census API page](https://api.census.gov/data/key_signup.html) to obtain an API key.

In addition, to understand how to configure the dataset path and query parameters, follow the guide and examples in the [API documentation](https://www.census.gov/data/developers/data-sets.html). Some particularly helpful pages:

- [Available Datasets](https://www.census.gov/data/developers/guidance/api-user-guide.Available_Data.html)
- [Core Concepts](https://www.census.gov/data/developers/guidance/api-user-guide.Core_Concepts.html)
- [Example Queries](https://www.census.gov/data/developers/guidance/api-user-guide.Example_API_Queries.html)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.2.0 | 2024-08-10 | [43521](https://github.com/airbytehq/airbyte/pull/43521) | Migrate to Low Code |
| 0.1.16 | 2024-08-10 | [43566](https://github.com/airbytehq/airbyte/pull/43566) | Update dependencies |
| 0.1.15 | 2024-08-03 | [43214](https://github.com/airbytehq/airbyte/pull/43214) | Update dependencies |
| 0.1.14 | 2024-07-27 | [42595](https://github.com/airbytehq/airbyte/pull/42595) | Update dependencies |
| 0.1.13 | 2024-07-20 | [42176](https://github.com/airbytehq/airbyte/pull/42176) | Update dependencies |
| 0.1.12 | 2024-07-13 | [41904](https://github.com/airbytehq/airbyte/pull/41904) | Update dependencies |
| 0.1.11 | 2024-07-10 | [41491](https://github.com/airbytehq/airbyte/pull/41491) | Update dependencies |
| 0.1.10 | 2024-07-09 | [41166](https://github.com/airbytehq/airbyte/pull/41166) | Update dependencies |
| 0.1.9 | 2024-07-06 | [40772](https://github.com/airbytehq/airbyte/pull/40772) | Update dependencies |
| 0.1.8 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.7 | 2024-06-25 | [40294](https://github.com/airbytehq/airbyte/pull/40294) | Update dependencies |
| 0.1.6 | 2024-06-22 | [39981](https://github.com/airbytehq/airbyte/pull/39981) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39262](https://github.com/airbytehq/airbyte/pull/39262) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-20 | [38370](https://github.com/airbytehq/airbyte/pull/38370) | [autopull] base image + poetry + up_to_date |
| 0.1.3 | 2024-01-03 | [33890](https://github.com/airbytehq/airbyte/pull/33890) | Allow additional properties in connector spec |
| 0.1.2 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Update fields in source-connectors specifications |
| 0.1.1 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0 | 2021-07-20 | [4228](https://github.com/airbytehq/airbyte/pull/4228) | Initial release |

</details>
