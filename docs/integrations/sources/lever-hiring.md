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
| 0.3.1 | 2024-06-04 | [39082](https://github.com/airbytehq/airbyte/pull/39082) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.0 | 2024-05-08 | [36262](https://github.com/airbytehq/airbyte/pull/36262) | Migrate to Low Code |
| 0.2.0 | 2023-05-25 | [26564](https://github.com/airbytehq/airbyte/pull/26564) | Migrate to advancedAuth |
| 0.1.3 | 2022-10-14 | [17996](https://github.com/airbytehq/airbyte/pull/17996) | Add Basic Auth management |
| 0.1.2 | 2021-12-30 | [9214](https://github.com/airbytehq/airbyte/pull/9214) | Update title and descriptions |
| 0.1.1 | 2021-12-16 | [7677](https://github.com/airbytehq/airbyte/pull/7677) | OAuth Automated Authentication |
| 0.1.0 | 2021-09-22 | [6141](https://github.com/airbytehq/airbyte/pull/6141) | Add Lever Hiring Source Connector |

</details>
