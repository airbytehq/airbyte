# Lever Hiring

## Sync overview

The Lever Hiring source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Lever Hiring API](https://hire.lever.co/developer/documentation#introduction).

### Output schema

This Source is capable of syncing the following core Streams:

- [Applications](https://hire.lever.co/developer/documentation#list-all-applications)
- [Interviews](https://hire.lever.co/developer/documentation#list-all-interviews)
- [Notes](https://hire.lever.co/developer/documentation#list-all-notes)
- [Offers](https://hire.lever.co/developer/documentation#list-all-offers)
- [Opportunities](https://hire.lever.co/developer/documentation#list-all-opportunities)
- [Referrals](https://hire.lever.co/developer/documentation#list-all-referrals)
- [Users](https://hire.lever.co/developer/documentation#list-all-users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| SSL connection            | Yes                  |       |
| Namespaces                | No                   |       |

### Performance considerations

The Lever Hiring connector should not run into Lever Hiring API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Lever Hiring Client Id
- Lever Hiring Client Secret
- Lever Hiring Refresh Token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------|
| 0.4.21 | 2025-12-09 | [70794](https://github.com/airbytehq/airbyte/pull/70794) | Update dependencies |
| 0.4.20 | 2025-11-25 | [69501](https://github.com/airbytehq/airbyte/pull/69501) | Update dependencies |
| 0.4.19 | 2025-10-29 | [68936](https://github.com/airbytehq/airbyte/pull/68936) | Update dependencies |
| 0.4.18 | 2025-10-21 | [68331](https://github.com/airbytehq/airbyte/pull/68331) | Update dependencies |
| 0.4.17 | 2025-10-14 | [68064](https://github.com/airbytehq/airbyte/pull/68064) | Update dependencies |
| 0.4.16 | 2025-10-07 | [67526](https://github.com/airbytehq/airbyte/pull/67526) | Update dependencies |
| 0.4.15 | 2025-09-30 | [66814](https://github.com/airbytehq/airbyte/pull/66814) | Update dependencies |
| 0.4.14 | 2025-09-24 | [66648](https://github.com/airbytehq/airbyte/pull/66648) | Update dependencies |
| 0.4.13 | 2025-09-09 | [66083](https://github.com/airbytehq/airbyte/pull/66083) | Update dependencies |
| 0.4.12 | 2025-08-23 | [65324](https://github.com/airbytehq/airbyte/pull/65324) | Update dependencies |
| 0.4.11 | 2025-08-09 | [64602](https://github.com/airbytehq/airbyte/pull/64602) | Update dependencies |
| 0.4.10 | 2025-08-02 | [64302](https://github.com/airbytehq/airbyte/pull/64302) | Update dependencies |
| 0.4.9 | 2025-07-26 | [63847](https://github.com/airbytehq/airbyte/pull/63847) | Update dependencies |
| 0.4.8 | 2025-07-19 | [63519](https://github.com/airbytehq/airbyte/pull/63519) | Update dependencies |
| 0.4.7 | 2025-07-12 | [63111](https://github.com/airbytehq/airbyte/pull/63111) | Update dependencies |
| 0.4.6 | 2025-07-05 | [62598](https://github.com/airbytehq/airbyte/pull/62598) | Update dependencies |
| 0.4.5 | 2025-06-28 | [62189](https://github.com/airbytehq/airbyte/pull/62189) | Update dependencies |
| 0.4.4 | 2025-06-21 | [61808](https://github.com/airbytehq/airbyte/pull/61808) | Update dependencies |
| 0.4.3 | 2025-06-14 | [48264](https://github.com/airbytehq/airbyte/pull/48264) | Update dependencies |
| 0.4.2 | 2024-10-28 | [43750](https://github.com/airbytehq/airbyte/pull/43750) | Update dependencies |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-15 | [44133](https://github.com/airbytehq/airbyte/pull/44133) | Refactor connector to manifest-only format |
| 0.3.1 | 2024-06-04 | [39082](https://github.com/airbytehq/airbyte/pull/39082) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.0 | 2024-05-08 | [36262](https://github.com/airbytehq/airbyte/pull/36262) | Migrate to Low Code |
| 0.2.0 | 2023-05-25 | [26564](https://github.com/airbytehq/airbyte/pull/26564) | Migrate to advancedAuth |
| 0.1.3 | 2022-10-14 | [17996](https://github.com/airbytehq/airbyte/pull/17996) | Add Basic Auth management |
| 0.1.2 | 2021-12-30 | [9214](https://github.com/airbytehq/airbyte/pull/9214) | Update title and descriptions |
| 0.1.1 | 2021-12-16 | [7677](https://github.com/airbytehq/airbyte/pull/7677) | OAuth Automated Authentication |
| 0.1.0 | 2021-09-22 | [6141](https://github.com/airbytehq/airbyte/pull/6141) | Add Lever Hiring Source Connector |

</details>
