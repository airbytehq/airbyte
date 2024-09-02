# Partnerstack

## Sync overview

The Partnerstack source supports both Full Refresh only.

This source can sync data for the [Partnerstack API](https://docs.partnerstack.com/reference).

### Output schema

This Source is capable of syncing the following core Streams:

- [Customers](https://docs.partnerstack.com/reference/get_v2-customers-2)
- [Deals](https://docs.partnerstack.com/reference/get_v2-deals)
- [Groups](https://docs.partnerstack.com/reference/get_v2-groups)
- [Leads](https://docs.partnerstack.com/reference/get_v2-leads)
- [Partnerships](https://docs.partnerstack.com/reference/get_v2-partnerships-2)
- [Rewards](https://docs.partnerstack.com/reference/get_v2-rewards-2)
- [Transactions](https://docs.partnerstack.com/reference/get_v2-transactions-2)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Partnerstack connector should not run into Partnerstack API limitations under normal usage.

## Requirements

- **Partnerstack API keys**. See the [Partnerstack docs](https://docs.partnerstack.com/reference/auth) for information on how to obtain the API keys.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------|
| 0.1.16 | 2024-08-31 | [45053](https://github.com/airbytehq/airbyte/pull/45053) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44712](https://github.com/airbytehq/airbyte/pull/44712) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44358](https://github.com/airbytehq/airbyte/pull/44358) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43738](https://github.com/airbytehq/airbyte/pull/43738) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43692](https://github.com/airbytehq/airbyte/pull/43692) | Update dependencies |
| 0.1.11 | 2024-08-03 | [42757](https://github.com/airbytehq/airbyte/pull/42757) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42338](https://github.com/airbytehq/airbyte/pull/42338) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41757](https://github.com/airbytehq/airbyte/pull/41757) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41466](https://github.com/airbytehq/airbyte/pull/41466) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41306](https://github.com/airbytehq/airbyte/pull/41306) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40881](https://github.com/airbytehq/airbyte/pull/40881) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40378](https://github.com/airbytehq/airbyte/pull/40378) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40024](https://github.com/airbytehq/airbyte/pull/40024) | Update dependencies |
| 0.1.3 | 2024-06-13 | [37595](https://github.com/airbytehq/airbyte/pull/37595) | Change `last_records` to `last_record` |
| 0.1.2 | 2024-06-04 | [38964](https://github.com/airbytehq/airbyte/pull/38964) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38484](https://github.com/airbytehq/airbyte/pull/38484) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-27 | [XXX](https://github.com/airbytehq/airbyte/pull/XXX)     | Add Partnerstack Source Connector           |

</details>
