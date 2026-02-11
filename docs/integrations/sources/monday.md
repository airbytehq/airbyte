# Monday

This page contains the setup guide and reference information for the [Monday](https://monday.com/) source connector.

## Prerequisites

To set up the Monday source connector, you need one of the following:

- A **Personal API Token** from your Monday.com account, or
- **OAuth 2.0** credentials (Client ID, Client Secret, and Access Token) from a Monday.com OAuth application

To find your personal API token, open your Monday.com account and click your profile picture. Select **Developers** to open the Developer Center, then click **API token** > **Show**. Account admins can also access their token by selecting **Administration** > **API** from the profile menu. For more details, see the [Monday.com authentication guide](https://developer.monday.com/api-reference/docs/authentication).

To use OAuth 2.0, you need a Monday.com OAuth application. Open your profile picture, select **Developers** > **My Apps**, and select your app to find the Client ID and Client Secret.

## Setup guide

### Step 1: Create the source in Airbyte

<!-- env:cloud -->
1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
<!-- /env:cloud -->
<!-- env:oss -->
1. Log into your Airbyte Self-Managed instance.
<!-- /env:oss -->
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Monday** from the list of available sources.

### Step 2: Authenticate

#### Connect using OAuth 2.0

1. Select **OAuth 2.0** in **Authorization Method**.
2. Click **Authenticate your Monday account**.
3. Complete the authentication flow using your Monday.com credentials.

#### Connect using API token

1. Select **API Token** in **Authorization Method**.
2. Enter your personal API token. To find it, see the Monday.com [authentication guide](https://developer.monday.com/api-reference/docs/authentication).

### Step 3: Configure optional settings

<FieldAnchor field="board_ids">

Optionally, enter specific **Board IDs** to limit the Items and Boards streams to specific boards. When left empty, the connector syncs all boards in your account.

</FieldAnchor>

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
- [Boards](https://developer.monday.com/api-reference/docs/boards)
- [Teams](https://developer.monday.com/api-reference/docs/teams-queries)
- [Updates](https://developer.monday.com/api-reference/docs/updates-queries)
- [Users](https://developer.monday.com/api-reference/docs/users-queries-1)
- [Tags](https://developer.monday.com/api-reference/docs/tags-queries)
- [Workspaces](https://developer.monday.com/api-reference/docs/workspaces)

### Notes on streams

- The `Boards` stream includes `Columns` data for each board. In your destination, this data typically appears as a nested table such as `boards.columns`.

- The `Items` stream includes `Column Values` for each item (row) on a board. In your destination, this data typically appears as a nested table such as `items.column_values`. The `display_value` field is available for Mirror, Dependency, and Connect Board column types.

- Incremental sync for the `Items` and `Boards` streams uses the `Activity logs` stream. Board and item IDs are extracted from activity log events and used to selectively sync updated boards and items. If the time between incremental syncs is longer than the activity logs retention period for your Monday.com plan, some data may not be captured. Check your plan's retention period at [monday.com/pricing](https://monday.com/pricing).

If there are additional endpoints you'd like Airbyte to support, [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

## Performance considerations

The Monday connector should not run into Monday.com API limitations under normal usage. The connector automatically retries requests when it encounters complexity budget or rate limit errors.

Monday.com's API uses a [complexity-based rate limiting system](https://developer.monday.com/api-reference/docs/rate-limits). Each query consumes complexity points, and your account has a per-minute complexity budget that varies by plan. If you experience rate limit issues that are not automatically retried successfully, [create an issue](https://github.com/airbytehq/airbyte/issues).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                              | Subject                                                                                                                                                                |
|:-----------|:-----------|:----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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
