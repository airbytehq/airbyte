# Aha API
API Documentation link [here](https://www.aha.io/api)
## Overview

The Aha API source supports full refresh syncs

### Output schema

Two output streams are available from this source:

*[features](https://www.aha.io/api/resources/features/list_features).
*[products](https://www.aha.io/api/resources/products/list_products_in_the_account).

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Rate Limiting information is updated [here](https://www.aha.io/api#rate-limiting).

## Getting started

### Requirements

* Aha API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://www.aha.io/api#authentication).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.3.1   | 2023-06-05 | [27002](https://github.com/airbytehq/airbyte/pull/27002) | Flag spec `api_key` field as `airbyte-secret` |
| 0.3.0   | 2023-05-30 | [22642](https://github.com/airbytehq/airbyte/pull/22642) | Add `idea_comments`, `idea_endorsements`, and `idea_categories` streams |
| 0.2.0   | 2023-05-26 | [26666](https://github.com/airbytehq/airbyte/pull/26666) | Fix integration test and schemas                |
| 0.1.0   | 2022-11-02 | [18883](https://github.com/airbytehq/airbyte/pull/18893) | 🎉 New Source: Aha                              |
