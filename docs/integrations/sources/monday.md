# Monday

## Prerequisites

* Monday API Token / Monday Access Token

You can find your Oauth application in Monday main page -> Profile picture (bottom left corner) -> Developers -> My Apps -> Select your app.

You can get the API token for Monday by going to Profile picture (bottom left corner) -> Admin -> API.

## Setup guide

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Monday connector and select **Monday** from the Source type dropdown.
4. Fill in your API Key or authenticate using OAuth and then click **Set up source**.

### Connect using `OAuth 2.0` option:
1. Select `OAuth2.0` in `Authorization Method`.
2. Click on `authenticate your Monday account`.
2. Proceed the authentication using your credentials for your Monday account.

### Connect using `API Token` option:
1. Generate an API Token as described [here](https://developer.monday.com/api-reference/docs/authentication).
2. Use the generated `api_token` in the Airbyte connection.

## Supported sync modes

The Monday supports full refresh syncs

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

## Supported Streams

Several output streams are available from this source:

* [Items](https://developer.monday.com/api-reference/docs/items-queries)
* [Boards](https://developer.monday.com/api-reference/docs/groups-queries#groups-queries)
* [Teams](https://developer.monday.com/api-reference/docs/teams-queries)
* [Updates](https://developer.monday.com/api-reference/docs/updates-queries)
* [Users](https://developer.monday.com/api-reference/docs/users-queries-1)
* [Tags](https://developer.monday.com/api-reference/docs/tags-queries)
* [Workspaces](https://developer.monday.com/api-reference/docs/workspaces)

Important Notes:
* `Columns` are available from the `Boards` stream. By syncing the `Boards` stream you will get the `Columns` for each `Board` synced in the database
The typical name of the table depends on the `destination` you use like `boards.columns`, for instance.

* `Column Values` are  available from the `Items` stream. By syncing  the `Items` stream you will get the `Column Values` for each `Item` (row) of the board.
The typical name of the table depends on the `destination` you use like `items.column_values`, for instance.


If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)


## Performance considerations

The Monday connector should not run into Monday API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 1.0.0   | 2023-06-20 | [27410](https://github.com/airbytehq/airbyte/pull/27410) | Add new streams: Tags, Workspaces. Add new fields for existing streams. |
| 0.2.6   | 2023-06-12 | [27244](https://github.com/airbytehq/airbyte/pull/27244) | Added http error handling for `403` and `500` HTTP errors               |  
| 0.2.5   | 2023-05-22 | [225881](https://github.com/airbytehq/airbyte/pull/25881) | Fix pagination for the items stream                                     |  
| 0.2.4   | 2023-04-26 | [25277](https://github.com/airbytehq/airbyte/pull/25277) | Increase row limit to 100                                               |
| 0.2.3   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version                                 |
| 0.2.2   | 2023-01-04 | [20996](https://github.com/airbytehq/airbyte/pull/20996) | Fix json schema loader                                                  |
| 0.2.1   | 2022-12-15 | [20533](https://github.com/airbytehq/airbyte/pull/20533) | Bump CDK version                                                        |
| 0.2.0   | 2022-12-13 | [19586](https://github.com/airbytehq/airbyte/pull/19586) | Migrate to low-code                                                     |
| 0.1.4   | 2022-06-06 | [14443](https://github.com/airbytehq/airbyte/pull/14443) | Increase retry_factor for Items stream                                  |
| 0.1.3   | 2021-12-23 | [8172](https://github.com/airbytehq/airbyte/pull/8172)   | Add oauth2.0 support                                                    |
| 0.1.2   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                                          |
| 0.1.1   | 2021-11-18 | [8016](https://github.com/airbytehq/airbyte/pull/8016)   | 🐛 Source Monday: fix pagination and schema bug                         |
| 0.1.0   | 2021-11-07 | [7168](https://github.com/airbytehq/airbyte/pull/7168)   | 🎉 New Source: Monday                                                   |
