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
| :------------------------ |:---------------------| :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Requirements

- **Klaus API keys**. See the [Klaus API docs](https://support.klausapp.com/en/articles/4027272-setting-up-a-custom-integration) for information on how to obtain the API keys.

## Changelog

| Version | Date       | Pull Request                                             | Subject                        |
| :------ |:-----------| :------------------------------------------------------- |:-------------------------------|
| 0.1.4 | 2024-04-19 | [37183](https://github.com/airbytehq/airbyte/pull/37183) | Updating to 0.80.0 CDK |
| 0.1.3 | 2024-04-18 | [37183](https://github.com/airbytehq/airbyte/pull/37183) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37183](https://github.com/airbytehq/airbyte/pull/37183) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37183](https://github.com/airbytehq/airbyte/pull/37183) | schema descriptions |
| 0.1.0 | 2023-05-04 | [25790](https://github.com/airbytehq/airbyte/pull/25790) | Add Klaus API Source Connector |
