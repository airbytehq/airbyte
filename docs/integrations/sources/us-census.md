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

| Version | Date       | Pull Request                                           | Subject                                           |
| :------ | :--------- | :----------------------------------------------------- | :------------------------------------------------ |
| 0.1.2   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Update fields in source-connectors specifications |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies                   |
| 0.1.0   | 2021-07-20 | [4228](https://github.com/airbytehq/airbyte/pull/4228) | Initial release                                   |
