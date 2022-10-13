# Monday

## Overview

The Monday supports full refresh syncs

### Output schema

Several output streams are available from this source:

* [Items](https://api.developer.monday.com/docs/items-queries)
* [Boards](https://api.developer.monday.com/docs/groups-queries#groups-queries)
* [Teams](https://api.developer.monday.com/docs/teams-queries)
* [Updates](https://api.developer.monday.com/docs/updates-queries)
* [Users](https://api.developer.monday.com/docs/users-queries-1)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The Monday connector should not run into Monday API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Monday API Token

OR
* Monday Access Token

### Connect using `OAuth 2.0` option:
1. Select `OAuth2.0` in `Authorization Method`..
2. Click on `authenticate your Monday account`.
2. Proceed the authentication using your credentials for your Monday account.

### Connect using `API Token` option:
1. Generate an API Token as described [here](https://api.developer.monday.com/docs/authentication).
2. Use the generated `api_token` in the Airbyte connection.

### Setup guide

You can find your Oauth application in Monday main page -> Profile picture (bottom left corner) -> Developers -> My Apps -> Select your app.

You can get the API token for Monday by going to Profile picture (bottom left corner) -> Admin -> API.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.4   | 2022-06-06 | [14443](https://github.com/airbytehq/airbyte/pull/14443) | Increase retry_factor for Items stream          |
| 0.1.3   | 2021-12-23 | [8172](https://github.com/airbytehq/airbyte/pull/8172)   | Add oauth2.0 support                            |
| 0.1.2   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                  |
| 0.1.1   | 2021-11-18 | [8016](https://github.com/airbytehq/airbyte/pull/8016)   | 🐛 Source Monday: fix pagination and schema bug |
| 0.1.0   | 2021-11-07 | [7168](https://github.com/airbytehq/airbyte/pull/7168)   | 🎉 New Source: Monday                           |
