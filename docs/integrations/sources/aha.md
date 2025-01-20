# Aha API

API Documentation link [here](https://www.aha.io/api)

## Overview

The Aha API source supports full refresh syncs

### Output schema

Two output streams are available from this source:

_[features](https://www.aha.io/api/resources/features/list_features).
_[products](https://www.aha.io/api/resources/products/list_products_in_the_account).

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Rate Limiting information is updated [here](https://www.aha.io/api#rate-limiting).

## Getting started

### Requirements

- Aha API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://www.aha.io/api#authentication).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------| :------------------------------------------------------- |:------------------------------------------------------------------------|
| 0.4.10 | 2025-01-18 | [51732](https://github.com/airbytehq/airbyte/pull/51732) | Update dependencies |
| 0.4.9 | 2025-01-11 | [51234](https://github.com/airbytehq/airbyte/pull/51234) | Update dependencies |
| 0.4.8 | 2024-12-28 | [50490](https://github.com/airbytehq/airbyte/pull/50490) | Update dependencies |
| 0.4.7 | 2024-12-21 | [50158](https://github.com/airbytehq/airbyte/pull/50158) | Update dependencies |
| 0.4.6 | 2024-12-14 | [49548](https://github.com/airbytehq/airbyte/pull/49548) | Update dependencies |
| 0.4.5 | 2024-12-12 | [49298](https://github.com/airbytehq/airbyte/pull/49298) | Update dependencies |
| 0.4.4 | 2024-12-11 | [48246](https://github.com/airbytehq/airbyte/pull/48246) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.3 | 2024-10-29 | [47904](https://github.com/airbytehq/airbyte/pull/47904) | Update dependencies |
| 0.4.2 | 2024-10-28 | [47641](https://github.com/airbytehq/airbyte/pull/47641) | Update dependencies |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-14 | [44042](https://github.com/airbytehq/airbyte/pull/44042) | Refactor connector to manifest-only format |
| 0.3.14 | 2024-08-12 | [43748](https://github.com/airbytehq/airbyte/pull/43748) | Update dependencies |
| 0.3.13 | 2024-08-10 | [43556](https://github.com/airbytehq/airbyte/pull/43556) | Update dependencies |
| 0.3.12 | 2024-08-03 | [43186](https://github.com/airbytehq/airbyte/pull/43186) | Update dependencies |
| 0.3.11 | 2024-07-27 | [42737](https://github.com/airbytehq/airbyte/pull/42737) | Update dependencies |
| 0.3.10 | 2024-07-20 | [42306](https://github.com/airbytehq/airbyte/pull/42306) | Update dependencies |
| 0.3.9 | 2024-07-13 | [41914](https://github.com/airbytehq/airbyte/pull/41914) | Update dependencies |
| 0.3.8 | 2024-07-10 | [41568](https://github.com/airbytehq/airbyte/pull/41568) | Update dependencies |
| 0.3.7 | 2024-07-09 | [41170](https://github.com/airbytehq/airbyte/pull/41170) | Update dependencies |
| 0.3.6 | 2024-07-06 | [40774](https://github.com/airbytehq/airbyte/pull/40774) | Update dependencies |
| 0.3.5 | 2024-06-25 | [40435](https://github.com/airbytehq/airbyte/pull/40435) | Update dependencies |
| 0.3.4 | 2024-06-22 | [40000](https://github.com/airbytehq/airbyte/pull/40000) | Update dependencies |
| 0.3.3 | 2024-06-06 | [39153](https://github.com/airbytehq/airbyte/pull/39153) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.2 | 2024-05-14 | [38144](https://github.com/airbytehq/airbyte/pull/38144) | Make connector compatible with Builder |
| 0.3.1 | 2023-06-05 | [27002](https://github.com/airbytehq/airbyte/pull/27002) | Flag spec `api_key` field as `airbyte-secret` |
| 0.3.0 | 2023-05-30 | [22642](https://github.com/airbytehq/airbyte/pull/22642) | Add `idea_comments`, `idea_endorsements`, and `idea_categories` streams |
| 0.2.0 | 2023-05-26 | [26666](https://github.com/airbytehq/airbyte/pull/26666) | Fix integration test and schemas |
| 0.1.0   | 2022-11-02 | [18883](https://github.com/airbytehq/airbyte/pull/18893) | 🎉 New Source: Aha                                                      |

</details>
