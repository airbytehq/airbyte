# New York Times

## Overview

The New York Times source supports full refresh syncs

### Output schema

Several output streams are available from this source:

_[Archive](https://developer.nytimes.com/docs/archive-product/1/overview).
_[Most Popular Emailed Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/emailed/%7Bperiod%7D.json/get).
_[Most Popular Shared Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/shared/%7Bperiod%7D.json/get).
_[Most Popular Viewed Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/viewed/%7Bperiod%7D.json/get).

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

### Performance considerations

The New York Times connector should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- New York Times API Key.

### Connect using `API Key`:

1. Create a new App [here](https://developer.nytimes.com/my-apps/new-app) (You need to have an account to create a new App).
2. Enable API access for the supported endpoints (see Output schema section for supported streams).
3. Write the key into `secrets/config.json` file.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.2 | 2024-10-29 | [47728](https://github.com/airbytehq/airbyte/pull/47728) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47634](https://github.com/airbytehq/airbyte/pull/47634) | Update dependencies |
| 0.2.0 | 2024-08-22 | [44555](https://github.com/airbytehq/airbyte/pull/44555) | Refactor connector to manifest-only format |
| 0.1.18 | 2024-08-17 | [44349](https://github.com/airbytehq/airbyte/pull/44349) | Update dependencies |
| 0.1.17 | 2024-08-10 | [43577](https://github.com/airbytehq/airbyte/pull/43577) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43257](https://github.com/airbytehq/airbyte/pull/43257) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42733](https://github.com/airbytehq/airbyte/pull/42733) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42234](https://github.com/airbytehq/airbyte/pull/42234) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41912](https://github.com/airbytehq/airbyte/pull/41912) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41580](https://github.com/airbytehq/airbyte/pull/41580) | Update dependencies |
| 0.1.11 | 2024-07-10 | [41102](https://github.com/airbytehq/airbyte/pull/41102) | Update dependencies |
| 0.1.10 | 2024-07-08 | [41030](https://github.com/airbytehq/airbyte/pull/41030) | Fix spec by removing invalid date properties |
| 0.1.9 | 2024-07-06 | [40955](https://github.com/airbytehq/airbyte/pull/40955) | Update dependencies |
| 0.1.8 | 2024-06-25 | [40390](https://github.com/airbytehq/airbyte/pull/40390) | Update dependencies |
| 0.1.7 | 2024-06-22 | [40079](https://github.com/airbytehq/airbyte/pull/40079) | Update dependencies |
| 0.1.6   | 2024-06-5  | [39119](https://github.com/airbytehq/airbyte/pull/39119)     | Upgrade base image to 1.2.2                                                     |
| 0.1.5   | 2024-04-19 | [37204](https://github.com/airbytehq/airbyte/pull/37204) | Updating to 0.80.0 CDK                                                          |
| 0.1.4   | 2024-04-18 | [37204](https://github.com/airbytehq/airbyte/pull/37204) | Manage dependencies with Poetry.                                                |
| 0.1.3   | 2024-04-15 | [37204](https://github.com/airbytehq/airbyte/pull/37204) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2   | 2024-04-12 | [37204](https://github.com/airbytehq/airbyte/pull/37204) | schema descriptions                                                             |
| 0.1.1   | 2023-02-13 | [22925](https://github.com/airbytehq/airbyte/pull/22925) | Specified date formatting in specification                                      |
| 0.1.0   | 2022-11-01 | [18746](https://github.com/airbytehq/airbyte/pull/18746) | 🎉 New Source: New York Times                                                  |

</details>
