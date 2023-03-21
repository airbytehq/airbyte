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

| Version | Date       | Pull Request                                           | Subject         |
| :------ | :--------- | :----------------------------------------------------- | :-------------- |
| 0.1.1   | Unknown    | Unknown                                                | Bump Version    |
| 0.1.0   | 2021-10-14 | [7062](https://github.com/airbytehq/airbyte/pull/7062) | Initial Release |
