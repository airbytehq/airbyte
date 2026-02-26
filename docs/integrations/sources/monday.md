# Monday

This page contains the setup guide and reference information for the [Monday](https://monday.com/) source connector.

This connector uses the [Monday.com GraphQL API](https://developer.monday.com/api-reference/docs) (version 2026-01).

## Prerequisites

To set up the Monday source connector, you need either:

- A **Personal API Token**, which you can generate from your Monday.com account under **Profile picture** (bottom left corner) > **Admin** > **API**.
- An **OAuth 2.0 application**, which you can find or create under **Profile picture** (bottom left corner) > **Developers** > **My Apps**.

For more details, see Monday.com's [authentication documentation](https://developer.monday.com/api-reference/docs/authentication).

## Setup guide

1. In Airbyte, navigate to **Sources** and click **+ New source**.
2. Search for and select **Monday**.
3. Enter a name for the connector.
4. Choose your authentication method and enter the required credentials.
5. Optionally, enter one or more **Board IDs** to limit syncing to specific boards. If left empty, the connector syncs data from all boards in your account.
6. Click **Set up source**.

### Connect using OAuth 2.0

1. Select **OAuth2.0** in **Authorization Method**.
2. Click **Authenticate your Monday account**.
3. Complete the authentication flow using your Monday.com credentials.

### Connect using API Token

1. Generate an API token as described in Monday.com's [authentication documentation](https://developer.monday.com/api-reference/docs/authentication).
2. Select **API Token** in **Authorization Method**.
3. Enter your token in the **Personal API Token** field.

## Supported sync modes

The Monday source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | No         |

## Supported streams

The following streams are available:

| Stream | Sync mode | API documentation |
| :--- | :--- | :--- |
| Activity logs | Full Refresh, Incremental | [Activity logs](https://developer.monday.com/api-reference/docs/activity-logs) |
| Boards | Full Refresh, Incremental | [Boards](https://developer.monday.com/api-reference/docs/boards) |
| Items | Full Refresh, Incremental | [Items](https://developer.monday.com/api-reference/docs/items-queries) |
| Tags | Full Refresh | [Tags](https://developer.monday.com/api-reference/docs/tags-queries) |
| Teams | Full Refresh | [Teams](https://developer.monday.com/api-reference/docs/teams-queries) |
| Updates | Full Refresh | [Updates](https://developer.monday.com/api-reference/docs/updates-queries) |
| Users | Full Refresh | [Users](https://developer.monday.com/api-reference/docs/users-queries-1) |
| Workspaces | Full Refresh | [Workspaces](https://developer.monday.com/api-reference/docs/workspaces) |

### Stream notes

- The Boards stream includes column definitions for each board. In your destination, these appear as nested data, typically named `boards.columns`.

- The Items stream includes column values for each item. In your destination, these appear as nested data, typically named `items.column_values`.

- Incremental sync for the Items and Boards streams relies on the Activity logs stream. Board and item IDs are extracted from activity log events and used to selectively sync only the changed records. If the time between syncs exceeds the activity log retention period for your [Monday.com plan](https://monday.com/pricing), some changes may not be captured during incremental syncs.

If there are additional endpoints you'd like Airbyte to support, [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

## Performance considerations

The Monday connector should not run into Monday API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                              | Subject                                                                                                                                                                |
|:-----------|:-----------|:----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.5.2 | 2026-02-24 | [73582](https://github.com/airbytehq/airbyte/pull/73582) | Update dependencies |
| 2.5.1 | 2026-02-13 | [72192](https://github.com/airbytehq/airbyte/pull/72192) | Add `user_id` field to `activity_logs` stream |
| 2.5.0 | 2026-02-11 | [72832](https://github.com/airbytehq/airbyte/pull/72832) | Upgrade to Monday.com API version 2026-01 |
| 2.4.21 | 2026-02-10 | [73038](https://github.com/airbytehq/airbyte/pull/73038) | Update dependencies |
| 2.4.20 | 2026-02-03 | [72577](https://github.com/airbytehq/airbyte/pull/72577) | Update dependencies |
| 2.4.19 | 2026-01-20 | [71994](https://github.com/airbytehq/airbyte/pull/71994) | Update dependencies |
| 2.4.18 | 2026-01-14 | [71513](https://github.com/airbytehq/airbyte/pull/71513) | Update dependencies |
| 2.4.17 | 2025-12-18 | [70552](https://github.com/airbytehq/airbyte/pull/70552) | Update dependencies |
| 2.4.16 | 2025-12-03 | [69718](https://github.com/airbytehq/airbyte/pull/69718) | Add pagination reset handling for Monday CursorExpiredError |
| 2.4.15 | 2025-11-25 | [69883](https://github.com/airbytehq/airbyte/pull/69883) | Update dependencies |
| 2.4.14 | 2025-11-18 | [69367](https://github.com/airbytehq/airbyte/pull/69367) | Update dependencies |
| 2.4.13 | 2025-10-29 | [69048](https://github.com/airbytehq/airbyte/pull/69048) | Update dependencies |
| 2.4.12 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 2.4.11 | 2025-10-21 | [68416](https://github.com/airbytehq/airbyte/pull/68416) | Update dependencies |
| 2.4.10 | 2025-10-14 | [67840](https://github.com/airbytehq/airbyte/pull/67840) | Update dependencies |
| 2.4.9 | 2025-10-07 | [67393](https://github.com/airbytehq/airbyte/pull/67393) | Update dependencies |
| 2.4.8 | 2025-10-02 | [66938](https://github.com/airbytehq/airbyte/pull/66938) | Surface HTTP 200 Error Messages |
| 2.4.7 | 2025-09-30 | [66336](https://github.com/airbytehq/airbyte/pull/66336) | Update dependencies |
| 2.4.6 | 2025-09-10 | [65884](https://github.com/airbytehq/airbyte/pull/65884) | Update dependencies |
| 2.4.5 | 2025-08-23 | [64705](https://github.com/airbytehq/airbyte/pull/64705) | Update dependencies |
| 2.4.4 | 2025-08-11 | [64878](https://github.com/airbytehq/airbyte/pull/64878) | Pass query in json body of request instead of query params. |
| 2.4.3 | 2025-08-02 | [64220](https://github.com/airbytehq/airbyte/pull/64220) | Update dependencies |
| 2.4.2 | 2025-07-26 | [63835](https://github.com/airbytehq/airbyte/pull/63835) | Update dependencies |
| 2.4.1 | 2025-07-19 | [63206](https://github.com/airbytehq/airbyte/pull/63206) | Update dependencies |
| 2.4.0 | 2025-07-09 | [62886](https://github.com/airbytehq/airbyte/pull/62886) | Promoting release candidate 2.4.0-rc.1 to a main version. |
| 2.4.0-rc.1 | 2025-07-02 | [62444](https://github.com/airbytehq/airbyte/pull/62444)  | Migrate connector to manifest-only                                                                                                                                     |
| 2.3.1      | 2025-05-31 | [53828](https://github.com/airbytehq/airbyte/pull/53828)  | Update dependencies                                                                                                                                                    |
| 2.3.0      | 2025-04-02 | [56967](https://github.com/airbytehq/airbyte/pull/56967)  | Promoting release candidate 2.3.0-rc.1 to a main version.                                                                                                              |
| 2.3.0-rc.1 | 2025-03-18 | [55225](https://github.com/airbytehq/airbyte/pull/55225)  | Update CDK to v6                                                                                                                                                       |
| 2.2.0      | 2025-03-14 | [52780](https://github.com/airbytehq/airbyte/pull/52780)  | Add optional config parameter to control which boards are fetched when syncing the `Boards` stream                                                                     |
| 2.1.13     | 2025-02-01 | [52780](https://github.com/airbytehq/airbyte/pull/52780)  | Update dependencies                                                                                                                                                    |
| 2.1.12     | 2025-01-25 | [51833](https://github.com/airbytehq/airbyte/pull/51833)  | Update dependencies                                                                                                                                                    |
| 2.1.11     | 2025-01-14 | [10311](https://github.com/airbytehq/airbyte/pull/10311)  | Update API version to 2024-10                                                                                                                                          |
| 2.1.10     | 2025-01-11 | [51147](https://github.com/airbytehq/airbyte/pull/51147)  | Update dependencies                                                                                                                                                    |
| 2.1.9      | 2025-01-08 | [50984](https://github.com/airbytehq/airbyte/pull/50984)  | Update the `spec` to support `Jinja` style variables for `DeclarativeOAuthFlow`                                                                                        |
| 2.1.8      | 2024-12-28 | [50624](https://github.com/airbytehq/airbyte/pull/50624)  | Update dependencies                                                                                                                                                    |
| 2.1.7      | 2024-12-21 | [43901](https://github.com/airbytehq/airbyte/pull/43901)  | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.1.6      | 2024-12-19 | [49943](https://github.com/airbytehq/airbyte/pull/49943)  | Pin CDK constraint to avoid breaking change in newer versions                                                                                                          |
| 2.1.5      | 2024-10-31 | [48054](https://github.com/airbytehq/airbyte/pull/48054)  | Moved to `DeclarativeOAuthFlow` specification                                                                                                                          |
| 2.1.4      | 2024-08-17 | [44201](https://github.com/airbytehq/airbyte/pull/44201)  | Add boards name to the `items` stream                                                                                                                                  |
| 2.1.3      | 2024-06-04 | [38958](https://github.com/airbytehq/airbyte/pull/38958)  | [autopull] Upgrade base image to v1.2.1                                                                                                                                |
| 2.1.2      | 2024-04-30 | [37722](https://github.com/airbytehq/airbyte/pull/37722)  | Fetch `display_value` field for column values of `Mirror`, `Dependency` and `Connect Board` types                                                                      |
| 2.1.1      | 2024-04-05 | [36717](https://github.com/airbytehq/airbyte/pull/36717)  | Add handling of complexityBudgetExhausted error.                                                                                                                       |
| 2.1.0      | 2024-04-03 | [36746](https://github.com/airbytehq/airbyte/pull/36746)  | Pin airbyte-cdk version to `^0`                                                                                                                                        |
| 2.0.4      | 2024-02-28 | [35696](https://github.com/airbytehq/airbyte/pull/35696)  | Fix extraction for `null` value in stream `Activity logs`                                                                                                              |
| 2.0.3      | 2024-02-21 | [35506](https://github.com/airbytehq/airbyte/pull/35506)  | Support for column values of the mirror type for the `Items` stream.                                                                                                   |
| 2.0.2      | 2024-02-12 | [35146](https://github.com/airbytehq/airbyte/pull/35146)  | Manage dependencies with Poetry.                                                                                                                                       |
| 2.0.1      | 2024-02-08 | [35016](https://github.com/airbytehq/airbyte/pull/35016)  | Migrated to the latest airbyte cdk                                                                                                                                     |
| 2.0.0      | 2024-01-12 | [34108](https://github.com/airbytehq/airbyte/pull/34108)  | Migrated to the latest API version: 2024-01                                                                                                                            |
| 1.1.4      | 2023-12-13 | [33448](https://github.com/airbytehq/airbyte/pull/33448)  | Increase test coverage and migrate to base image                                                                                                                       |
| 1.1.3      | 2023-09-23 | [30248](https://github.com/airbytehq/airbyte/pull/30248)  | Add new field "type" to board stream                                                                                                                                   |
| 1.1.2      | 2023-08-23 | [29777](https://github.com/airbytehq/airbyte/pull/29777)  | Add retry for `502` error                                                                                                                                              |
| 1.1.1      | 2023-08-15 | [29429](https://github.com/airbytehq/airbyte/pull/29429)  | Ignore `null` records in response                                                                                                                                      |
| 1.1.0      | 2023-07-05 | [27944](https://github.com/airbytehq/airbyte/pull/27944)  | Add incremental sync for Items and Boards streams                                                                                                                      |
| 1.0.0      | 2023-06-20 | [27410](https://github.com/airbytehq/airbyte/pull/27410)  | Add new streams: Tags, Workspaces. Add new fields for existing streams.                                                                                                |
| 0.2.6      | 2023-06-12 | [27244](https://github.com/airbytehq/airbyte/pull/27244)  | Added http error handling for `403` and `500` HTTP errors                                                                                                              |
| 0.2.5      | 2023-05-22 | [25881](https://github.com/airbytehq/airbyte/pull/25881) | Fix pagination for the items stream                                                                                                                                    |
| 0.2.4      | 2023-04-26 | [25277](https://github.com/airbytehq/airbyte/pull/25277)  | Increase row limit to 100                                                                                                                                              |
| 0.2.3      | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231)  | Publish using low-code CDK Beta version                                                                                                                                |
| 0.2.2      | 2023-01-04 | [20996](https://github.com/airbytehq/airbyte/pull/20996)  | Fix json schema loader                                                                                                                                                 |
| 0.2.1      | 2022-12-15 | [20533](https://github.com/airbytehq/airbyte/pull/20533)  | Bump CDK version                                                                                                                                                       |
| 0.2.0      | 2022-12-13 | [19586](https://github.com/airbytehq/airbyte/pull/19586)  | Migrate to low-code                                                                                                                                                    |
| 0.1.4      | 2022-06-06 | [14443](https://github.com/airbytehq/airbyte/pull/14443)  | Increase retry_factor for Items stream                                                                                                                                 |
| 0.1.3      | 2021-12-23 | [8172](https://github.com/airbytehq/airbyte/pull/8172)    | Add oauth2.0 support                                                                                                                                                   |
| 0.1.2      | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429)    | Update titles and descriptions                                                                                                                                         |
| 0.1.1      | 2021-11-18 | [8016](https://github.com/airbytehq/airbyte/pull/8016)    | 🐛 Source Monday: fix pagination and schema bug                                                                                                                        |
| 0.1.0      | 2021-11-07 | [7168](https://github.com/airbytehq/airbyte/pull/7168)    | 🎉 New Source: Monday                                                                                                                                                  |

</details>
