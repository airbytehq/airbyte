# Freshcaller

## Overview

The Freshcaller source supports full refresh and incremental sync. Depending on your needs, one could choose appropriate sync mode - `full refresh` replicates all records every time a sync happens where as `incremental` replicates net-new records since the last successful sync.

### Output schema

The following endpoints are supported from this source:

- [Users](https://developers.freshcaller.com/api/#users)
- [Teams](https://developers.freshcaller.com/api/#teams)
- [Calls](https://developers.freshcaller.com/api/#calls)
- [Call Metrics](https://developers.freshcaller.com/api/#call-metrics)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

### Performance considerations

The Freshcaller connector should not run into Freshcaller API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Freshcaller Account
- Freshcaller API Key

### Setup guide

Please read [How to find your API key](https://support.freshdesk.com/en/support/solutions/articles/225435-where-can-i-find-my-api-key-).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.4.16 | 2024-10-12 | [46796](https://github.com/airbytehq/airbyte/pull/46796) | Update dependencies |
| 0.4.15 | 2024-10-05 | [46435](https://github.com/airbytehq/airbyte/pull/46435) | Update dependencies |
| 0.4.14 | 2024-09-28 | [46173](https://github.com/airbytehq/airbyte/pull/46173) | Update dependencies |
| 0.4.13 | 2024-09-21 | [45760](https://github.com/airbytehq/airbyte/pull/45760) | Update dependencies |
| 0.4.12 | 2024-09-14 | [45522](https://github.com/airbytehq/airbyte/pull/45522) | Update dependencies |
| 0.4.11 | 2024-09-07 | [45323](https://github.com/airbytehq/airbyte/pull/45323) | Update dependencies |
| 0.4.10 | 2024-08-31 | [44973](https://github.com/airbytehq/airbyte/pull/44973) | Update dependencies |
| 0.4.9 | 2024-08-24 | [44718](https://github.com/airbytehq/airbyte/pull/44718) | Update dependencies |
| 0.4.8 | 2024-08-17 | [44256](https://github.com/airbytehq/airbyte/pull/44256) | Update dependencies |
| 0.4.7 | 2024-08-10 | [43691](https://github.com/airbytehq/airbyte/pull/43691) | Update dependencies |
| 0.4.6 | 2024-08-03 | [43238](https://github.com/airbytehq/airbyte/pull/43238) | Update dependencies |
| 0.4.5 | 2024-07-27 | [42676](https://github.com/airbytehq/airbyte/pull/42676) | Update dependencies |
| 0.4.4 | 2024-07-20 | [42196](https://github.com/airbytehq/airbyte/pull/42196) | Update dependencies |
| 0.4.3 | 2024-07-13 | [41821](https://github.com/airbytehq/airbyte/pull/41821) | Update dependencies |
| 0.4.2 | 2024-07-10 | [41552](https://github.com/airbytehq/airbyte/pull/41552) | Update dependencies |
| 0.4.1 | 2024-07-09 | [41195](https://github.com/airbytehq/airbyte/pull/41195) | Update dependencies |
| 0.4.0 | 2024-03-07 | [35892](https://github.com/airbytehq/airbyte/pull/35892) | ✨ Source: add `life_cycle` to `call_metrics` stream |
| 0.3.3 | 2024-07-06 | [40843](https://github.com/airbytehq/airbyte/pull/40843) | Update dependencies |
| 0.3.2 | 2024-07-01 | [40618](https://github.com/airbytehq/airbyte/pull/40618) | Migrate to base image and poetry, update CDK |
| 0.3.1 | 2023-11-28 | [32874](https://github.com/airbytehq/airbyte/pull/32874) | 🐛 Source: fix page_size_option parameter in spec |
| 0.3.0   | 2023-10-24 | [31102](https://github.com/airbytehq/airbyte/pull/14759) | ✨ Source: Migrate to Low Code CDK                |
| 0.2.0   | 2023-05-15 | [26065](https://github.com/airbytehq/airbyte/pull/26065) | Fix spec type check for `start_date`              |
| 0.1.0   | 2022-08-11 | [14759](https://github.com/airbytehq/airbyte/pull/14759) | 🎉 New Source: Freshcaller                        |

</details>
