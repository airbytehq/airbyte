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
| 0.1.3   | 2024-06-13 | [37595](https://github.com/airbytehq/airbyte/pull/37595) | Change `last_records` to `last_record`      |
| 0.1.2   | 2024-06-04 | [38964](https://github.com/airbytehq/airbyte/pull/38964) | [autopull] Upgrade base image to v1.2.1     |
| 0.1.1   | 2024-05-21 | [38484](https://github.com/airbytehq/airbyte/pull/38484) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-27 | [XXX](https://github.com/airbytehq/airbyte/pull/XXX)     | Add Partnerstack Source Connector           |

</details>
