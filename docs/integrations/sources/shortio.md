# Shortio

## Sync overview

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shortio API](https://developers.short.io/reference).

### Output schema

This Source is capable of syncing the following Streams:

- [Clicks](https://developers.short.io/reference#getdomaindomainidlink_clicks)
- [Links](https://developers.short.io/reference#apilinksget)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Getting started

1. Sign in at `app.short.io`.
2. Go to settings and click on `Integrations & API`.
3. In the API tab, click `Create API Kay`. Select `Private Key`.
4. Use the created secret key to configure your source!

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.3.15 | 2025-02-22 | [54502](https://github.com/airbytehq/airbyte/pull/54502) | Update dependencies |
| 0.3.14 | 2025-02-15 | [54092](https://github.com/airbytehq/airbyte/pull/54092) | Update dependencies |
| 0.3.13 | 2025-02-08 | [53528](https://github.com/airbytehq/airbyte/pull/53528) | Update dependencies |
| 0.3.12 | 2025-02-01 | [53100](https://github.com/airbytehq/airbyte/pull/53100) | Update dependencies |
| 0.3.11 | 2025-01-25 | [52412](https://github.com/airbytehq/airbyte/pull/52412) | Update dependencies |
| 0.3.10 | 2025-01-18 | [52007](https://github.com/airbytehq/airbyte/pull/52007) | Update dependencies |
| 0.3.9 | 2025-01-11 | [51396](https://github.com/airbytehq/airbyte/pull/51396) | Update dependencies |
| 0.3.8 | 2024-12-28 | [50820](https://github.com/airbytehq/airbyte/pull/50820) | Update dependencies |
| 0.3.7 | 2024-12-21 | [50316](https://github.com/airbytehq/airbyte/pull/50316) | Update dependencies |
| 0.3.6 | 2024-12-14 | [49760](https://github.com/airbytehq/airbyte/pull/49760) | Update dependencies |
| 0.3.5 | 2024-12-12 | [49422](https://github.com/airbytehq/airbyte/pull/49422) | Update dependencies |
| 0.3.4 | 2024-12-11 | [48178](https://github.com/airbytehq/airbyte/pull/48178) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.3 | 2024-10-29 | [47858](https://github.com/airbytehq/airbyte/pull/47858) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47564](https://github.com/airbytehq/airbyte/pull/47564) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-14 | [44066](https://github.com/airbytehq/airbyte/pull/44066) | Refactor connector to manifest-only format |
| 0.2.13 | 2024-08-12 | [43852](https://github.com/airbytehq/airbyte/pull/43852) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43602](https://github.com/airbytehq/airbyte/pull/43602) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43167](https://github.com/airbytehq/airbyte/pull/43167) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42750](https://github.com/airbytehq/airbyte/pull/42750) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42288](https://github.com/airbytehq/airbyte/pull/42288) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41931](https://github.com/airbytehq/airbyte/pull/41931) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41489](https://github.com/airbytehq/airbyte/pull/41489) | Update dependencies |
| 0.2.6 | 2024-07-09 | [40877](https://github.com/airbytehq/airbyte/pull/40877) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40309](https://github.com/airbytehq/airbyte/pull/40309) | Update dependencies |
| 0.2.4 | 2024-06-22 | [40099](https://github.com/airbytehq/airbyte/pull/40099) | Update dependencies |
| 0.2.3 | 2024-06-05 | [38842](https://github.com/airbytehq/airbyte/pull/38842) | Embed schemas and spec |
| 0.2.2 | 2024-06-04 | [38970](https://github.com/airbytehq/airbyte/pull/38970) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-02 | [37597](https://github.com/airbytehq/airbyte/pull/37597) | Change `last_records` to `last_record` |
| 0.2.0 | 2023-08-02 | [28950](https://github.com/airbytehq/airbyte/pull/28950) | Migrate to Low-Code CDK |
| 0.1.3 | 2022-08-01 | [15066](https://github.com/airbytehq/airbyte/pull/15066) | Update primary key to `idString` |
| 0.1.2 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Update fields in source-connectors specifications |
| 0.1.1 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0   | 2021-08-16 | [3787](https://github.com/airbytehq/airbyte/pull/5418)   | Add Native Shortio Source Connector               |

</details>
