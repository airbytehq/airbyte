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

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.1.0   | 2023-05-04 | [25790](https://github.com/airbytehq/airbyte/pull/25790) | Add Klaus API Source Connector |
