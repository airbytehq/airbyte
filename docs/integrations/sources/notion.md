# Notion

This page contains the setup guide and reference information for the Notion source connector.

## Prerequisites

- Access to a [Notion](https://notion.so/login) workspace
- To authenticate with an access token, or with your own OAuth connection in Airbyte Open Source, you must be a [Workspace Owner](https://www.notion.com/help/add-members-admins-guests-and-groups) in Notion so you can create a connection

## Setup guide

To authenticate the Notion source connector, use **one** of the following methods:

- OAuth2.0 authorization (recommended for Airbyte Cloud)
- Access Token

Notion calls the apps that access its API _connections_. You manage them in the Notion [Developer portal](https://app.notion.com/developers/connections). For more detail, see Notion's [internal connections](https://developers.notion.com/guides/get-started/internal-connections) and [public connections](https://developers.notion.com/guides/get-started/public-connections) guides.

<!-- env:cloud -->

:::note
**For Airbyte Cloud users:** If you use OAuth2.0 authorization in Airbyte Cloud, you don't need to create a connection in Notion. Skip to [setting up the connector in Airbyte](#step-3-set-up-the-notion-connector-in-airbyte).
:::

<!-- /env:cloud -->

### Step 1: Create a connection in Notion and set capabilities {#step-1-create-an-integration-in-notion}

1. Open the Notion [Developer portal](https://app.notion.com/developers/connections). In the **Build** section of the sidebar, select **Internal connections**.
2. Click **Create a new connection**, enter a name, and choose the workspace you want to sync.
3. Open the connection's **Configuration** tab and enable the following [capabilities](https://developers.notion.com/reference/capabilities) based on the streams you want to sync:

   - **Read content**: Required for all connections.
   - **Read comments**: Required for the Comments stream.
   - **Read user information** (with or without email addresses): Required for the Users stream.

### Step 2: Share pages and get your credentials {#step-2-set-permissions-and-acquire-authorization-credentials}

#### Access Token (Cloud and Open Source)

The connector only syncs pages and data sources that you share with your connection. Sharing a page also shares all of its child pages.

1. Share the pages you want to sync with your connection. Use either method:
   - In the Developer portal, open your connection, click the **Content access** tab, click **Edit access**, and select the pages and databases to share.
   - In Notion, open a page, click the **•••** menu in the top-right corner, select **Connections**, click **+ Add connection**, and choose your connection.
2. In the connection's **Configuration** tab, copy the **API token**. Then continue to [setting up the connector in Airbyte](#step-3-set-up-the-notion-connector-in-airbyte).

<!-- env:oss -->

#### OAuth2.0 (Open Source only)

To use OAuth2.0 in Airbyte Open Source, create a public connection instead of an internal connection, then complete Notion's OAuth flow to get an access token.

1. In the [Developer portal](https://app.notion.com/developers/connections), in the **Build** section of the sidebar, select **Public connections**, then click **Create new connection**.
2. Fill in the required fields, including a redirect URI, and enable the capabilities listed in [Step 1](#step-1-create-an-integration-in-notion).
3. In the connection's **Configuration** tab, copy the **OAuth client ID** and **OAuth client secret**.
4. Use the connection's authorization URL to choose the pages to share and exchange the returned code for an access token. Notion's [authorization guide](https://developers.notion.com/guides/get-started/authorization#public-connection-auth-flow-set-up) explains each step. When you have your client ID, client secret, and access token, continue to the next step.
<!-- /env:oss -->

### Step 3: Set up the Notion connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **New source**.
3. Find and select **Notion** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Choose the method of authentication from the dropdown menu:

<!-- env:cloud -->

#### Authentication for Airbyte Cloud

- **OAuth2.0** (Recommended): Click **Authenticate your Notion account**. When the popup appears, click **Select pages**. Check the pages you want to give Airbyte access to, and click **Allow access**.
- **Access Token**: Paste the API token from your internal connection's **Configuration** tab.
<!-- /env:cloud -->

<!-- env:oss -->

#### Authentication for Airbyte Open Source

- **Access Token**: Paste the API token from your internal connection's **Configuration** tab.
- **OAuth2.0**: Paste the client ID, client secret, and access token from your public connection.
<!-- /env:oss -->

6. (Optional) Enter a **Start Date** in UTC, in the format `YYYY-MM-DDTHH:mm:ss.SSSZ`. The connector doesn't sync records last edited before this date. If you leave it blank, the start date defaults to two years before the current date.
7. (Optional) Set **Number of concurrent workers** to control how many requests the connector makes in parallel. The default is 3 and the maximum is 10. For guidance, see [Performance considerations](#performance-considerations).
8. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Notion source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Stream       | Full Refresh (Overwrite/Append) | Incremental (Append/Append + Deduped) |
|--------------|:-------------------------------:|:-------------------------------------:|
| Blocks       |                ✓                |                   ✓                   |
| Comments     |                ✓                |                   ✓                   |
| Data Sources |                ✓                |                   ✓                   |
| Pages        |                ✓                |                   ✓                   |
| Users        |                ✓                |                                       |

Incremental streams use the `last_edited_time` field as the cursor and filter records on the client side. On each sync, the connector reads records from Notion and only emits records edited since the last sync.

## Supported streams

The Notion source connector supports the following streams:

- [Blocks](https://developers.notion.com/reference/get-block-children): Retrieves content blocks for all synced pages, including recursively nested child blocks up to 30 levels deep. Block types `child_page`, `child_database`, and `ai_block` are excluded.
- [Comments](https://developers.notion.com/reference/list-comments): Retrieves un-resolved comments on all synced pages. Requires the **Read comments** capability.
- [Data Sources](https://developers.notion.com/reference/data-source): Retrieves all data sources shared with your connection, using the [Search](https://developers.notion.com/reference/post-search) endpoint. In Notion API version `2025-09-03`, a data source represents a structured table that contains pages and properties, previously called a "database." This stream replaces the former `Databases` stream as of v4.0.0. For details on migrating, see the [Notion migration guide](notion-migrations.md).
- [Pages](https://developers.notion.com/reference/page): Retrieves all pages shared with your connection, using the [Search](https://developers.notion.com/reference/post-search) endpoint.
- [Users](https://developers.notion.com/reference/get-users): Retrieves users in the workspace, including bots. Notion doesn't return guests from this endpoint. Requires the **Read user information** capability.

### Record format

The connector reshapes some fields so they have a consistent structure in your destination:

- **Pages** and **Data Sources**: Notion returns `properties` as an object keyed by property name. The connector converts it to an array of objects, each with a `name` field (the property name) and a `value` field (the property object Notion returned).
- **Users**: For bot users, Notion stores owner details under a key that matches the owner type, such as `bot.owner.workspace` or `bot.owner.user`. The connector moves these details to `bot.owner.info`. The `bot.owner.type` field still tells you the owner type.

## Performance considerations

Notion rate limits each connection to an average of three requests per second on most plans, and ten requests per second on Business and Enterprise plans. Notion also enforces a separate limit shared across all connections in a workspace. When the connector receives an HTTP 429 response, it waits for the time in the `Retry-After` header and retries the request. Rate-limited requests don't count toward the maximum retry limit, so syncs continue until the rate limit clears. For more details, see Notion's [request limits](https://developers.notion.com/reference/request-limits) documentation.

The connector sends requests in parallel. Use the **Number of concurrent workers** setting (1 to 10, default 3) to control parallelism. More workers can speed up large syncs, but make it more likely that the connector hits Notion's rate limits.

The Blocks stream recursively fetches child blocks up to 30 levels deep. Pages with deeply nested content can generate a large number of API requests, which can slow down syncs for workspaces with complex page structures. If Notion returns a 404 error because a block isn't shared with your connection, the connector skips that block instead of failing the sync.

## Troubleshooting

### Users stream fails with a permission error

If the Users stream fails with the message "Notion integration lacks read user information for the Users stream," your connection doesn't have the **Read user information** capability. Open your connection in the Notion [Developer portal](https://app.notion.com/developers/connections) and enable **Read user information** in the **Configuration** tab. If you don't need user data, disable the Users stream in your Airbyte connection instead.

Notion [personal access tokens](https://developers.notion.com/guides/get-started/personal-access-tokens) can't list workspace users. If you authenticate with a personal access token instead of an internal connection's API token, disable the Users stream.

### Pages or blocks are missing

The connector only syncs content that you share with your connection. If pages, data sources, or blocks are missing, confirm that you shared the parent page with your connection, or that you selected the page during the OAuth flow.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:------------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.0.28 | 2026-10-13 | [88131](https://github.com/airbytehq/airbyte/pull/88131) | Replace custom record transformations for the users, pages and data_sources streams with declarative components (no change to record output) |
| 4.0.27 | 2026-10-13 | [88718](https://github.com/airbytehq/airbyte/pull/88718) | Update dependencies |
| 4.0.26 | 2026-10-06 | [87944](https://github.com/airbytehq/airbyte/pull/87944) | Update dependencies |
| 4.0.25 | 2026-09-29 | [87242](https://github.com/airbytehq/airbyte/pull/87242) | Update dependencies |
| 4.0.24 | 2026-09-22 | [86721](https://github.com/airbytehq/airbyte/pull/86721) | Update dependencies |
| 4.0.23 | 2026-09-15 | [86135](https://github.com/airbytehq/airbyte/pull/86135) | Update dependencies |
| 4.0.22 | 2026-09-08 | [85579](https://github.com/airbytehq/airbyte/pull/85579) | Update dependencies |
| 4.0.21 | 2026-08-18 | [84680](https://github.com/airbytehq/airbyte/pull/84680) | Update dependencies |
| 4.0.20 | 2026-08-11 | [84017](https://github.com/airbytehq/airbyte/pull/84017) | Update dependencies |
| 4.0.19 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 4.0.18 | 2026-07-28 | [83183](https://github.com/airbytehq/airbyte/pull/83183) | Roll Cloud back to 4.0.16 — 4.0.17 is built on SDM 7.23.7, which breaks bundled custom components |
| 4.0.17 | 2026-07-28 | [83001](https://github.com/airbytehq/airbyte/pull/83001) | Update dependencies |
| 4.0.16 | 2026-07-21 | [82506](https://github.com/airbytehq/airbyte/pull/82506) | Update dependencies |
| 4.0.15 | 2026-07-14 | [81929](https://github.com/airbytehq/airbyte/pull/81929) | Update dependencies |
| 4.0.14 | 2026-06-30 | [81166](https://github.com/airbytehq/airbyte/pull/81166) | Update dependencies |
| 4.0.13 | 2026-06-23 | [80566](https://github.com/airbytehq/airbyte/pull/80566) | Update dependencies |
| 4.0.12 | 2026-06-16 | [79948](https://github.com/airbytehq/airbyte/pull/79948) | Update dependencies |
| 4.0.11 | 2026-06-09 | [79397](https://github.com/airbytehq/airbyte/pull/79397) | Update dependencies |
| 4.0.10 | 2026-06-02 | [78821](https://github.com/airbytehq/airbyte/pull/78821) | Update dependencies |
| 4.0.9 | 2026-06-01 | [78048](https://github.com/airbytehq/airbyte/pull/78048) | Improve the permission error message for the Users stream when the Notion integration lacks user information capabilities. |
| 4.0.8 | 2026-06-01 | [78543](https://github.com/airbytehq/airbyte/pull/78543) | Set final default concurrency to 3 with configurable worker count |
| 4.0.8-rc.5 | 2026-05-28 | [78467](https://github.com/airbytehq/airbyte/pull/78467) | Remove Notion API budget while keeping configurable worker count defaulted to 5 |
| 4.0.8-rc.4 | 2026-05-26 | [78433](https://github.com/airbytehq/airbyte/pull/78433) | Reduce default concurrency to 4 while preserving configurable worker count and Notion API budget |
| 4.0.8-rc.3 | 2026-05-22 | [78343](https://github.com/airbytehq/airbyte/pull/78343) | Revert default concurrency to 5, add configurable worker count, and enforce Notion API budget |
| 4.0.8-rc.2 | 2026-05-19 | [78274](https://github.com/airbytehq/airbyte/pull/78274) | Increase `default_concurrency` to 6 for concurrency tuning iteration 2 |
| 4.0.8-rc.1 | 2026-05-18 | [78149](https://github.com/airbytehq/airbyte/pull/78149) | Start concurrency tuning rollout |
| 4.0.7 | 2026-04-28 | [77340](https://github.com/airbytehq/airbyte/pull/77340) | Update dependencies |
| 4.0.6 | 2026-04-21 | [76681](https://github.com/airbytehq/airbyte/pull/76681) | Update dependencies |
| 4.0.5 | 2026-04-01 | [75577](https://github.com/airbytehq/airbyte/pull/75577) | Add `oauth_connector_input_specification` for declarative OAuth |
| 4.0.4 | 2026-03-31 | [75747](https://github.com/airbytehq/airbyte/pull/75747) | Update dependencies |
| 4.0.3 | 2026-03-30 | [75603](https://github.com/airbytehq/airbyte/pull/75603) | Fix 429 status code mapping from RETRY to RATE_LIMITED for improved rate limit handling and observability |
| 4.0.2 | 2026-03-23 | [75290](https://github.com/airbytehq/airbyte/pull/75290) | Update v4.0.0 upgrade deadline to 2026-04-10 |
| 4.0.1 | 2026-03-10 | [74616](https://github.com/airbytehq/airbyte/pull/74616) | Update dependencies |
| 4.0.0 | 2026-02-25 | [74017](https://github.com/airbytehq/airbyte/pull/74017) | Migrate to Notion API version 2025-09-03: replace `databases` stream with `data_sources`, update page parent references, and add new schema fields |
| 3.3.14 | 2026-02-24 | [73856](https://github.com/airbytehq/airbyte/pull/73856) | Update dependencies |
| 3.3.13 | 2026-02-10 | [73032](https://github.com/airbytehq/airbyte/pull/73032) | Update dependencies |
| 3.3.12 | 2026-02-09 | [72925](https://github.com/airbytehq/airbyte/pull/72925) | Add client-side incremental filtering to blocks stream RecordFilter |
| 3.3.11 | 2026-01-20 | [71943](https://github.com/airbytehq/airbyte/pull/71943) | Update dependencies |
| 3.3.10 | 2026-01-14 | [71602](https://github.com/airbytehq/airbyte/pull/71602) | Update dependencies |
| 3.3.9 | 2025-12-18 | [70534](https://github.com/airbytehq/airbyte/pull/70534) | Update dependencies |
| 3.3.8 | 2025-11-25 | [69853](https://github.com/airbytehq/airbyte/pull/69853) | Update dependencies |
| 3.3.7 | 2025-11-24 | [69780](https://github.com/airbytehq/airbyte/pull/69780) | Fix bug in current_block_depth |
| 3.3.6 | 2025-11-18 | [69375](https://github.com/airbytehq/airbyte/pull/69375) | Update dependencies |
| 3.3.5 | 2025-10-29 | [68750](https://github.com/airbytehq/airbyte/pull/68750) | Update dependencies |
| 3.3.4 | 2025-10-21 | [68399](https://github.com/airbytehq/airbyte/pull/68399) | Update dependencies |
| 3.3.3 | 2025-10-14 | [67801](https://github.com/airbytehq/airbyte/pull/67801) | Update dependencies |
| 3.3.2 | 2025-10-07 | [67422](https://github.com/airbytehq/airbyte/pull/67422) | Update dependencies |
| 3.3.1 | 2025-09-30 | [66927](https://github.com/airbytehq/airbyte/pull/66927) | Update dependencies |
| 3.3.0 | 2025-09-29 | [66734](https://github.com/airbytehq/airbyte/pull/66734) | Promoting release candidate 3.3.0-rc.1 to a main version. |
| 3.3.0-rc.1 | 2025-09-25 | [66532](https://github.com/airbytehq/airbyte/pull/66532) | Migrate to manifest-only. |
| 3.2.0 | 2025-09-25 | [66695](https://github.com/airbytehq/airbyte/pull/66695) | Promoting release candidate 3.2.0-rc.4 to a main version. |
| 3.2.0-rc.4 | 2025-09-24 | [66664](https://github.com/airbytehq/airbyte/pull/66664) | Handle 404 error and add sequence_number for blocks stream |
| 3.2.0-rc.3 | 2025-09-19 | [66539](https://github.com/airbytehq/airbyte/pull/66539) | Add default start date if not provided in the config to custom component |
| 3.2.0-rc.2 | 2025-09-19 | [66530](https://github.com/airbytehq/airbyte/pull/66530) | Add default start date if not provided in the config |
| 3.2.0-rc.1 | 2025-09-18 | [66191](https://github.com/airbytehq/airbyte/pull/66191) | Migrate Blocks stream to manifest. |
| 3.1.0 | 2025-07-30 | [55725](https://github.com/airbytehq/airbyte/pull/55725) | Add sequence_number to fetched Notion blocks |
| 3.0.16 | 2025-07-28 | [64102](https://github.com/airbytehq/airbyte/pull/64102) | Promoting release candidate 3.0.16-rc.1 to a main version. |
| 3.0.16-rc.1 | 2025-07-21 | [63368](https://github.com/airbytehq/airbyte/pull/63368) | Migrate to CDK V6 |
| 3.0.15 | 2025-07-19 | [63382](https://github.com/airbytehq/airbyte/pull/63382) | Update dependencies |
| 3.0.14 | 2025-07-12 | [63213](https://github.com/airbytehq/airbyte/pull/63213) | Update dependencies |
| 3.0.13 | 2025-07-05 | [62609](https://github.com/airbytehq/airbyte/pull/62609) | Update dependencies |
| 3.0.12 | 2025-06-24 | [62033](https://github.com/airbytehq/airbyte/pull/62033) | Add "in_trash" field in Notion "Pages" endpoint schema |
| 3.0.11 | 2025-06-28 | [62356](https://github.com/airbytehq/airbyte/pull/62356) | Update dependencies |
| 3.0.10 | 2025-06-21 | [61902](https://github.com/airbytehq/airbyte/pull/61902) | Update dependencies |
| 3.0.9 | 2025-06-14 | [61602](https://github.com/airbytehq/airbyte/pull/61602) | Update dependencies |
| 3.0.8 | 2025-06-07 | [52290](https://github.com/airbytehq/airbyte/pull/52290) | Update dependencies |
| 3.0.7 | 2025-01-11 | [43832](https://github.com/airbytehq/airbyte/pull/43832) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 3.0.6 | 2024-06-25 | [40498](https://github.com/airbytehq/airbyte/pull/40498) | Fix Pydantic error - add missing type annotation for `max_cursor_time` |
| 3.0.5 | 2024-06-04 | [38871](https://github.com/airbytehq/airbyte/pull/38871) | Refactor: use `client_side_incremental` feature |
| 3.0.4 | 2024-06-06 | [38798](https://github.com/airbytehq/airbyte/pull/38798) | Implement CheckpointMixin for state handling |
| 3.0.3 | 2024-06-06 | [39204](https://github.com/airbytehq/airbyte/pull/39204) | [autopull] Upgrade base image to v1.2.2 |
| 3.0.2 | 2024-05-20 | [38266](https://github.com/airbytehq/airbyte/pull/38266) | Replace AirbyteLogger with logging.Logger |
| 3.0.1 | 2024-04-24 | [36653](https://github.com/airbytehq/airbyte/pull/36653) | Schema descriptions and CDK 0.80.0 |
| 3.0.0 | 2024-04-12 | [35974](https://github.com/airbytehq/airbyte/pull/35974) | Migrate to low-code CDK (python CDK for Blocks stream) |
| 2.2.0 | 2024-04-08 | [36890](https://github.com/airbytehq/airbyte/pull/36890) | Unpin CDK version |
| 2.1.0 | 2024-02-19 | [35409](https://github.com/airbytehq/airbyte/pull/35409) | Update users stream schema with bot type info fields and block schema with mention type info fields. |
| 2.0.9 | 2024-02-12 | [35155](https://github.com/airbytehq/airbyte/pull/35155) | Manage dependencies with Poetry. |
| 2.0.8 | 2023-11-01 | [31899](https://github.com/airbytehq/airbyte/pull/31899) | Fix `table_row.cells` property in `Blocks` stream |
| 2.0.7 | 2023-10-31 | [32004](https://github.com/airbytehq/airbyte/pull/32004) | Reduce page_size on 504 errors |
| 2.0.6 | 2023-10-25 | [31825](https://github.com/airbytehq/airbyte/pull/31825) | Increase max_retries on retryable errors |
| 2.0.5 | 2023-10-23 | [31742](https://github.com/airbytehq/airbyte/pull/31742) | Add 'synced_block' property to Blocks schema |
| 2.0.4 | 2023-10-19 | [31625](https://github.com/airbytehq/airbyte/pull/31625) | Fix check_connection method |
| 2.0.3 | 2023-10-19 | [31612](https://github.com/airbytehq/airbyte/pull/31612) | Add exponential backoff for 500 errors |
| 2.0.2 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 2.0.1 | 2023-10-17 | [31507](https://github.com/airbytehq/airbyte/pull/31507) | Add start_date validation checks |
| 2.0.0 | 2023-10-09 | [30587](https://github.com/airbytehq/airbyte/pull/30587) | Source-wide schema update |
| 1.3.0 | 2023-10-09 | [30324](https://github.com/airbytehq/airbyte/pull/30324) | Add `Comments` stream |
| 1.2.2 | 2023-10-09 | [30780](https://github.com/airbytehq/airbyte/pull/30780) | Update Start Date in config to optional field |
| 1.2.1 | 2023-10-08 | [30750](https://github.com/airbytehq/airbyte/pull/30750) | Add availability strategy |
| 1.2.0 | 2023-10-04 | [31053](https://github.com/airbytehq/airbyte/pull/31053) | Add undeclared fields for blocks and pages streams |
| 1.1.2 | 2023-08-30 | [29999](https://github.com/airbytehq/airbyte/pull/29999) | Update error handling during connection check |
| 1.1.1 | 2023-06-14 | [26535](https://github.com/airbytehq/airbyte/pull/26535) | Migrate from deprecated `authSpecification` to `advancedAuth` |
| 1.1.0 | 2023-06-08 | [27170](https://github.com/airbytehq/airbyte/pull/27170) | Fix typo in `blocks` schema |
| 1.0.9 | 2023-06-08 | [27062](https://github.com/airbytehq/airbyte/pull/27062) | Skip streams with `invalid_start_cursor` error |
| 1.0.8 | 2023-06-07 | [27073](https://github.com/airbytehq/airbyte/pull/27073) | Add empty results handling for stream `Blocks` |
| 1.0.7 | 2023-06-06 | [27060](https://github.com/airbytehq/airbyte/pull/27060) | Add skipping 404 error in `Blocks` stream |
| 1.0.6 | 2023-05-18 | [26286](https://github.com/airbytehq/airbyte/pull/26286) | Add `parent` field to `Blocks` stream |
| 1.0.5 | 2023-05-01 | [25709](https://github.com/airbytehq/airbyte/pull/25709) | Fixed `ai_block is unsupported by API` issue, while fetching `Blocks` stream |
| 1.0.4 | 2023-04-11 | [25041](https://github.com/airbytehq/airbyte/pull/25041) | Improve error handling for API /search |
| 1.0.3 | 2023-03-02 | [22931](https://github.com/airbytehq/airbyte/pull/22931) | Specified date formatting in specification |
| 1.0.2 | 2023-02-24 | [23437](https://github.com/airbytehq/airbyte/pull/23437) | Add retry for 400 error (validation_error) |
| 1.0.1 | 2023-01-27 | [22018](https://github.com/airbytehq/airbyte/pull/22018) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 1.0.0 | 2022-12-19 | [20639](https://github.com/airbytehq/airbyte/pull/20639) | Fix `Pages` stream schema |
| 0.1.10 | 2022-09-28 | [17298](https://github.com/airbytehq/airbyte/pull/17298) | Use "Retry-After" header for backoff |
| 0.1.9 | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state |
| 0.1.8 | 2022-09-05 | [16272](https://github.com/airbytehq/airbyte/pull/16272) | Update spec description to include working timestamp example |
| 0.1.7 | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from shared schemas |
| 0.1.6 | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and spec |
| 0.1.5 | 2022-07-14 | [14706](https://github.com/airbytehq/airbyte/pull/14706) | Added OAuth2.0 authentication |
| 0.1.4 | 2022-07-07 | [14505](https://github.com/airbytehq/airbyte/pull/14505) | Fixed bug when normalization didn't run through |
| 0.1.3 | 2022-04-22 | [11452](https://github.com/airbytehq/airbyte/pull/11452) | Use pagination for User stream |
| 0.1.2 | 2022-01-11 | [9084](https://github.com/airbytehq/airbyte/pull/9084) | Fix documentation URL |
| 0.1.1 | 2021-12-30 | [9207](https://github.com/airbytehq/airbyte/pull/9207) | Update connector fields title/description |
| 0.1.0 | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092) | Initial Release |

</details>
