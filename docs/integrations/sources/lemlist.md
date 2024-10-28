# Lemlist

## Sync overview

The Lemlist source supports Full Refresh syncs only.

This source can sync data for the [Lemlist API](https://developer.lemlist.com/#introduction).

### Output schema

This Source is capable of syncing the following core Streams:

- Team `api.lemlist.com/api/team`
- Campaigns `api.lemlist.com/api/campaigns`
- Activities `api.lemlist.com/api/activities`
- Unsubscribes `api.lemlist.com/api/unsubscribes`

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Lemlist connector should not run into Lemlist API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Lemlist API key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                  |
| :------ | :--------- | :------------------------------------------------------- | :----------------------- |
| 0.3.1 | 2024-10-28 | [47652](https://github.com/airbytehq/airbyte/pull/47652) | Update dependencies |
| 0.3.0 | 2024-08-19 | [44413](https://github.com/airbytehq/airbyte/pull/44413) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-17 | [43880](https://github.com/airbytehq/airbyte/pull/43880) | Update dependencies |
| 0.2.13 | 2024-08-10 | [43586](https://github.com/airbytehq/airbyte/pull/43586) | Update dependencies |
| 0.2.12 | 2024-08-03 | [43050](https://github.com/airbytehq/airbyte/pull/43050) | Update dependencies |
| 0.2.11 | 2024-07-27 | [42768](https://github.com/airbytehq/airbyte/pull/42768) | Update dependencies |
| 0.2.10 | 2024-07-20 | [42152](https://github.com/airbytehq/airbyte/pull/42152) | Update dependencies |
| 0.2.9 | 2024-07-13 | [41872](https://github.com/airbytehq/airbyte/pull/41872) | Update dependencies |
| 0.2.8 | 2024-07-10 | [41415](https://github.com/airbytehq/airbyte/pull/41415) | Update dependencies |
| 0.2.7 | 2024-07-09 | [41309](https://github.com/airbytehq/airbyte/pull/41309) | Update dependencies |
| 0.2.6 | 2024-07-06 | [40942](https://github.com/airbytehq/airbyte/pull/40942) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40452](https://github.com/airbytehq/airbyte/pull/40452) | Update dependencies |
| 0.2.4 | 2024-06-22 | [39992](https://github.com/airbytehq/airbyte/pull/39992) | Update dependencies |
| 0.2.3 | 2024-06-06 | [39211](https://github.com/airbytehq/airbyte/pull/39211) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.2 | 2024-05-13 | [38119](https://github.com/airbytehq/airbyte/pull/38119) | Add builder compatability |
| 0.2.1 | 2024-05-15 | [37100](https://github.com/airbytehq/airbyte/pull/37100) | Add new A/B test columns |
| 0.2.0 | 2023-08-14 | [29406](https://github.com/airbytehq/airbyte/pull/29406) | Migrated to LowCode Cdk |
| 0.1.1   | Unknown    | Unknown                                                  | Bump Version             |
| 0.1.0   | 2021-10-14 | [7062](https://github.com/airbytehq/airbyte/pull/7062)   | Initial Release          |

</details>
