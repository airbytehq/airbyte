# Monday

This page contains the setup guide and reference information for the [Monday](https://monday.com/) source connector.

## Prerequisites

- Monday API Token / Monday Access Token

You can find your Oauth application in Monday main page -> Profile picture (bottom left corner) -> Developers -> My Apps -> Select your app.

You can get the API token for Monday by going to Profile picture (bottom left corner) -> Admin -> API.

## Setup guide

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Monday connector and select **Monday** from the Source type dropdown.
4. Fill in your API Key or authenticate using OAuth and then click **Set up source**.

### Connect using `OAuth 2.0` option

1. Select `OAuth2.0` in `Authorization Method`.
2. Click on `authenticate your Monday account`.
3. Proceed with the authentication using the credentials for your Monday account.

### Connect using `API Token` option

1. Generate an API Token as described [here](https://developer.monday.com/api-reference/docs/authentication).
2. Use the generated `api_token` in the Airbyte connection.

## Supported sync modes

The Monday source connector supports the following features:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | No         |
| Namespaces        | No         |

## Supported Streams

Several output streams are available from this source:

- [Activity logs](https://developer.monday.com/api-reference/docs/activity-logs)
- [Items](https://developer.monday.com/api-reference/docs/items-queries)
- [Boards](https://developer.monday.com/api-reference/docs/groups-queries#groups-queries)
- [Teams](https://developer.monday.com/api-reference/docs/teams-queries)
- [Updates](https://developer.monday.com/api-reference/docs/updates-queries)
- [Users](https://developer.monday.com/api-reference/docs/users-queries-1)
- [Tags](https://developer.monday.com/api-reference/docs/tags-queries)
- [Workspaces](https://developer.monday.com/api-reference/docs/workspaces)

Important Notes:

- `Columns` are available from the `Boards` stream. By syncing the `Boards` stream you will get the `Columns` for each `Board` synced in the database
  The typical name of the table depends on the `destination` you use like `boards.columns`, for instance.

- `Column Values` are available from the `Items` stream. By syncing the `Items` stream you will get the `Column Values` for each `Item` (row) of the board.
  The typical name of the table depends on the `destination` you use like `items.column_values`, for instance.
  If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

- Incremental sync for `Items` and `Boards` streams is done using the `Activity logs` stream.
  Ids of boards and items are extracted from activity logs events and used to selectively sync boards and items.
  Some data may be lost if the time between incremental syncs is longer than the activity logs retention time for your plan.
  Check your Monday plan at https://monday.com/pricing.

## Performance considerations

The Monday connector should not run into Monday API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                                           |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------ |
| 2.1.11 | 2025-01-14 | [51147](https://github.com/airbytehq/airbyte/pull/10311) | Update API version to 2024-10 |
| 2.1.10 | 2025-01-11 | [51147](https://github.com/airbytehq/airbyte/pull/51147) | Update dependencies |
| 2.1.9 | 2025-01-08 | [50984](https://github.com/airbytehq/airbyte/pull/50984) | Update the `spec` to support `Jinja` style variables for `DeclarativeOAuthFlow` |
| 2.1.8 | 2024-12-28 | [50624](https://github.com/airbytehq/airbyte/pull/50624) | Update dependencies |
| 2.1.7 | 2024-12-21 | [43901](https://github.com/airbytehq/airbyte/pull/43901) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.1.6 | 2024-12-19 | [49943](https://github.com/airbytehq/airbyte/pull/49943) | Pin CDK constraint to avoid breaking change in newer versions |
| 2.1.5 | 2024-10-31 | [48054](https://github.com/airbytehq/airbyte/pull/48054) | Moved to `DeclarativeOAuthFlow` specification |
| 2.1.4 | 2024-08-17 | [44201](https://github.com/airbytehq/airbyte/pull/44201) | Add boards name to the `items` stream |
| 2.1.3 | 2024-06-04 | [38958](https://github.com/airbytehq/airbyte/pull/38958) | [autopull] Upgrade base image to v1.2.1 |
| 2.1.2 | 2024-04-30 | [37722](https://github.com/airbytehq/airbyte/pull/37722) | Fetch `display_value` field for column values of `Mirror`, `Dependency` and `Connect Board` types |
| 2.1.1 | 2024-04-05 | [36717](https://github.com/airbytehq/airbyte/pull/36717) | Add handling of complexityBudgetExhausted error. |
| 2.1.0 | 2024-04-03 | [36746](https://github.com/airbytehq/airbyte/pull/36746) | Pin airbyte-cdk version to `^0` |
| 2.0.4 | 2024-02-28 | [35696](https://github.com/airbytehq/airbyte/pull/35696) | Fix extraction for `null` value in stream `Activity logs` |
| 2.0.3 | 2024-02-21 | [35506](https://github.com/airbytehq/airbyte/pull/35506) | Support for column values of the mirror type for the `Items` stream. |
| 2.0.2 | 2024-02-12 | [35146](https://github.com/airbytehq/airbyte/pull/35146) | Manage dependencies with Poetry. |
| 2.0.1 | 2024-02-08 | [35016](https://github.com/airbytehq/airbyte/pull/35016) | Migrated to the latest airbyte cdk |
| 2.0.0 | 2024-01-12 | [34108](https://github.com/airbytehq/airbyte/pull/34108) | Migrated to the latest API version: 2024-01 |
| 1.1.4 | 2023-12-13 | [33448](https://github.com/airbytehq/airbyte/pull/33448) | Increase test coverage and migrate to base image |
| 1.1.3 | 2023-09-23 | [30248](https://github.com/airbytehq/airbyte/pull/30248) | Add new field "type" to board stream |
| 1.1.2 | 2023-08-23 | [29777](https://github.com/airbytehq/airbyte/pull/29777) | Add retry for `502` error |
| 1.1.1 | 2023-08-15 | [29429](https://github.com/airbytehq/airbyte/pull/29429) | Ignore `null` records in response |
| 1.1.0 | 2023-07-05 | [27944](https://github.com/airbytehq/airbyte/pull/27944) | Add incremental sync for Items and Boards streams |
| 1.0.0 | 2023-06-20 | [27410](https://github.com/airbytehq/airbyte/pull/27410) | Add new streams: Tags, Workspaces. Add new fields for existing streams. |
| 0.2.6 | 2023-06-12 | [27244](https://github.com/airbytehq/airbyte/pull/27244) | Added http error handling for `403` and `500` HTTP errors |
| 0.2.5   | 2023-05-22 | [225881](https://github.com/airbytehq/airbyte/pull/25881) | Fix pagination for the items stream                                                               |
| 0.2.4   | 2023-04-26 | [25277](https://github.com/airbytehq/airbyte/pull/25277)  | Increase row limit to 100                                                                         |
| 0.2.3   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231)  | Publish using low-code CDK Beta version                                                           |
| 0.2.2   | 2023-01-04 | [20996](https://github.com/airbytehq/airbyte/pull/20996)  | Fix json schema loader                                                                            |
| 0.2.1   | 2022-12-15 | [20533](https://github.com/airbytehq/airbyte/pull/20533)  | Bump CDK version                                                                                  |
| 0.2.0   | 2022-12-13 | [19586](https://github.com/airbytehq/airbyte/pull/19586)  | Migrate to low-code                                                                               |
| 0.1.4   | 2022-06-06 | [14443](https://github.com/airbytehq/airbyte/pull/14443)  | Increase retry_factor for Items stream                                                            |
| 0.1.3   | 2021-12-23 | [8172](https://github.com/airbytehq/airbyte/pull/8172)    | Add oauth2.0 support                                                                              |
| 0.1.2   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429)    | Update titles and descriptions                                                                    |
| 0.1.1   | 2021-11-18 | [8016](https://github.com/airbytehq/airbyte/pull/8016)    | 🐛 Source Monday: fix pagination and schema bug                                                   |
| 0.1.0   | 2021-11-07 | [7168](https://github.com/airbytehq/airbyte/pull/7168)    | 🎉 New Source: Monday                                                                             |

</details>
