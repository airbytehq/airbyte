# Newsdata API

## Sync overview

This source retrieves the latests news from the [Newsdata API](https://newsdata.io/).

### Output schema

This source is capable of syncing the following streams:

- `latest`
- `sources`
  - **NOTE**: `category`, `language` and `country` input parameters only accept a single value, not multiple like `latest` stream.
    Thus, if several values are supplied, the first one will be the one to be used.

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? | Notes |
| :---------------- | ---------- | :---- |
| Full Refresh Sync | Yes        |       |
| Incremental Sync  | No         |       |

### Performance considerations

The News API free tier only allows 200 requests per day, and only up to 10
news per request.

The free tier does not allow to perform advanced search queries.

## Getting started

### Requirements

1. A Newsdata API key. You can get one [here](https://newsdata.io/register).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Newsdata API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.5 | 2024-06-06 | [39160](https://github.com/airbytehq/airbyte/pull/39160) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-28 | [38731](https://github.com/airbytehq/airbyte/pull/38731) | Make compatible with the builder |
| 0.1.3 | 2024-04-19 | [37203](https://github.com/airbytehq/airbyte/pull/37203) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37203](https://github.com/airbytehq/airbyte/pull/37203) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37203](https://github.com/airbytehq/airbyte/pull/37203) | schema descriptions |
| 0.1.0 | 2022-10-21 | [18576](https://github.com/airbytehq/airbyte/pull/18576) | 🎉 New Source: Newsdata |

</details>
