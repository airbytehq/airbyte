# Notion

This page contains the setup guide and reference information for the Notion source connector.

## Setup guide​

### Step 1: Set up Notion​

1. Create a new integration on the [My integrations](https://www.notion.so/my-integrations) page.

:::note

You must be the owner of a Notion workspace to create a new integration.

:::

2. Fill out the form. Make sure to check **Read content** and check any other [capabilities](https://developers.notion.com/reference/capabilities) you want to authorize.
3. Click **Submit**.
4. In the **Integration type** section, select either **Internal integration** (token authorization) or **Public integration** (OAuth2.0 authentication).
5. Check the capabilities you want to authorize.
6. If you select **Public integration**, fill out the fields in the **OAuth Domain & URIs** section.
7. Click **Save changes**.
8. Copy the Internal Access Token if you are using the [internal integration](https://developers.notion.com/docs/authorization#authorizing-internal-integrations), or copy the `access_token`, `client_id`, and `client_secret` if you are using the [public integration](https://developers.notion.com/docs/authorization#authorizing-public-integrations).

### Step 2: Set up the Notion connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Notion** from the **Source type** dropdown.
4. Enter a name for your source.
5. Choose the method of authentication:
      * If you select **Access Token**, paste the access token from [Step 8](#step-1-set-up-notion​).
      * If you select **OAuth2.0** authorization, click **Authenticate your Notion account**.
          * Log in and Authorize the Notion account. Select the permissions you want to allow Airbyte.
6. Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Notion** from the **Source type** dropdown.
4. Enter a name for your source.
5. Choose the method of authentication:
      * If you select **Access Token**, paste the access token from [Step 8](#step-1-set-up-notion​).
      * If you select **OAuth2.0** authorization, paste the client ID, access token, and client secret from [Step 8](#step-1-set-up-notion​).
6. Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Notion source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (partially)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The Notion source connector supports the following streams. For more information, see the [Notion API](https://developers.notion.com/reference/intro).

* [blocks](https://developers.notion.com/reference/retrieve-a-block)
* [databases](https://developers.notion.com/reference/retrieve-a-database)
* [pages](https://developers.notion.com/reference/retrieve-a-page)
* [users](https://developers.notion.com/reference/get-user)

:::note

The users stream does not support Incremental - Append sync mode.

:::

## Performance considerations

The connector is restricted by Notion [request limits](https://developers.notion.com/reference/request-limits). The Notion connector should not run into Notion API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                         |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------|
| 1.0.1   | 2023-01-27 | [22018](https://github.com/airbytehq/airbyte/pull/22018) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 1.0.0   | 2022-12-19 | [20639](https://github.com/airbytehq/airbyte/pull/20639) | Fix `Pages` stream schema                                       |
| 0.1.10  | 2022-09-28 | [17298](https://github.com/airbytehq/airbyte/pull/17298) | Use "Retry-After" header for backoff                            |
| 0.1.9   | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state                                     |
| 0.1.8   | 2022-09-05 | [16272](https://github.com/airbytehq/airbyte/pull/16272) | Update spec description to include working timestamp example    |
| 0.1.7   | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from shared schemas |
| 0.1.6   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and spec       |
| 0.1.5   | 2022-07-14 | [14706](https://github.com/airbytehq/airbyte/pull/14706) | Added OAuth2.0 authentication                                   |
| 0.1.4   | 2022-07-07 | [14505](https://github.com/airbytehq/airbyte/pull/14505) | Fixed bug when normalization didn't run through                 |
| 0.1.3   | 2022-04-22 | [11452](https://github.com/airbytehq/airbyte/pull/11452) | Use pagination for User stream                                  |
| 0.1.2   | 2022-01-11 | [9084](https://github.com/airbytehq/airbyte/pull/9084)   | Fix documentation URL                                           |
| 0.1.1   | 2021-12-30 | [9207](https://github.com/airbytehq/airbyte/pull/9207)   | Update connector fields title/description                       |
| 0.1.0   | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092)   | Initial Release                                                 |
