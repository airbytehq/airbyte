# Klaus API

## Sync overview

The Klaus API source supports both Full Refresh only.

This source can sync data for the [Klaus API](https://support.klausapp.com/en/collections/2212726-integrating-manually),
[Klaus Swagger](https://pub.klausapp.com/?urls.primaryName=Public%20API)

### Output schema

This Source is capable of syncing the following core Streams:

- [users](https://pub.klausapp.com/?urls.primaryName=Public%20API#/PublicApi/PublicApi_UsersV2)
- [categories](https://pub.klausapp.com/?urls.primaryName=Public%20API#/PublicApi/PublicApi_RatingCategoriesV2)
- [reviews](https://pub.klausapp.com/?urls.primaryName=Public%20API#/PublicApi/PublicApi_ReviewsV2)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Requirements

- **Klaus API keys**. See the [Klaus API docs](https://support.klausapp.com/en/articles/4027272-setting-up-a-custom-integration) for information on how to obtain the API keys.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.2.5 | 2025-03-08 | [55458](https://github.com/airbytehq/airbyte/pull/55458) | Update dependencies |
| 0.2.4 | 2025-03-01 | [54826](https://github.com/airbytehq/airbyte/pull/54826) | Update dependencies |
| 0.2.3 | 2025-02-22 | [54306](https://github.com/airbytehq/airbyte/pull/54306) | Update dependencies |
| 0.2.2 | 2025-02-15 | [52263](https://github.com/airbytehq/airbyte/pull/52263) | Update dependencies |
| 0.2.1 | 2025-01-18 | [47921](https://github.com/airbytehq/airbyte/pull/47921) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44764](https://github.com/airbytehq/airbyte/pull/44764) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-24 | [44719](https://github.com/airbytehq/airbyte/pull/44719) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44281](https://github.com/airbytehq/airbyte/pull/44281) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43842](https://github.com/airbytehq/airbyte/pull/43842) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43689](https://github.com/airbytehq/airbyte/pull/43689) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43285](https://github.com/airbytehq/airbyte/pull/43285) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42813](https://github.com/airbytehq/airbyte/pull/42813) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42170](https://github.com/airbytehq/airbyte/pull/42170) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41724](https://github.com/airbytehq/airbyte/pull/41724) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41353](https://github.com/airbytehq/airbyte/pull/41353) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41210](https://github.com/airbytehq/airbyte/pull/41210) | Update dependencies |
| 0.1.5 | 2024-07-06 | [41009](https://github.com/airbytehq/airbyte/pull/41009) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40296](https://github.com/airbytehq/airbyte/pull/40296) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40188](https://github.com/airbytehq/airbyte/pull/40188) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39208](https://github.com/airbytehq/airbyte/pull/39208) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38393](https://github.com/airbytehq/airbyte/pull/38393) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2023-05-04 | [25790](https://github.com/airbytehq/airbyte/pull/25790) | Add Klaus API Source Connector |

</details>
