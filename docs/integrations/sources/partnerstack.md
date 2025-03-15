# Partnerstack

## Sync overview

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
| Incremental - Append Sync | Yes                  |       |
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
| 0.3.2 | 2025-03-08 | [55537](https://github.com/airbytehq/airbyte/pull/55537) | Update dependencies |
| 0.3.1 | 2025-03-01 | [53962](https://github.com/airbytehq/airbyte/pull/53962) | Update dependencies |
| 0.3.0 | 2025-02-26 | [47280](https://github.com/airbytehq/airbyte/pull/47280) | Migrate to Manifest-only |
| 0.2.8 | 2025-02-01 | [52541](https://github.com/airbytehq/airbyte/pull/52541) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51913](https://github.com/airbytehq/airbyte/pull/51913) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51344](https://github.com/airbytehq/airbyte/pull/51344) | Update dependencies |
| 0.2.5 | 2025-01-04 | [50934](https://github.com/airbytehq/airbyte/pull/50934) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50723](https://github.com/airbytehq/airbyte/pull/50723) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50246](https://github.com/airbytehq/airbyte/pull/50246) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49675](https://github.com/airbytehq/airbyte/pull/49675) | Update dependencies |
| 0.2.1 | 2024-12-11 | [49085](https://github.com/airbytehq/airbyte/pull/49085) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.0 | 2024-12-03 | [48782](https://github.com/airbytehq/airbyte/pull/48782) | Add Incremental feature |
| 0.1.25 | 2024-11-04 | [48184](https://github.com/airbytehq/airbyte/pull/48184) | Update dependencies |
| 0.1.24 | 2024-10-29 | [47762](https://github.com/airbytehq/airbyte/pull/47762) | Update dependencies |
| 0.1.23 | 2024-10-28 | [47045](https://github.com/airbytehq/airbyte/pull/47045) | Update dependencies |
| 0.1.22 | 2024-10-12 | [46808](https://github.com/airbytehq/airbyte/pull/46808) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46452](https://github.com/airbytehq/airbyte/pull/46452) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46111](https://github.com/airbytehq/airbyte/pull/46111) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45775](https://github.com/airbytehq/airbyte/pull/45775) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45506](https://github.com/airbytehq/airbyte/pull/45506) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45294](https://github.com/airbytehq/airbyte/pull/45294) | Update dependencies |
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
