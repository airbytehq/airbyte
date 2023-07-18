# Notion

This page contains the setup guide and reference information for the Notion source connector.

## Prerequisites
- Access to a Notion workspace

## Setup guide​

To authenticate the Notion source connector, you need to use **one** of the following two methods:
- OAuth2.0 authorization (recommended for Airbyte Cloud)
- Access Token

:::note
**For Airbyte Cloud users:** We highly recommend using OAuth2.0 authorization to connect to Notion, as this method significantly simplifies the setup process. If you use OAuth2.0 authorization in Airbyte Cloud, you do **not** need to create and configure a new integration in Notion. Instead, you can proceed straight to 
[setting up the connector in Airbyte](#step-3-set-up-the-notion-connector-in-airbyte).
:::

We have provided a quick setup guide for creating an integration in Notion below. If you would like more detailed information and context on Notion integrations, or experience any difficulties with the integration setup process, please refer to the 
[official Notion documentation](https://developers.notion.com/docs).

### Step 1: Create an integration in Notion​

1. Log in to your Notion workspace and navigate to the [My integrations](https://www.notion.so/my-integrations) page. Select **+ New integration**.

:::note
You must be the owner of the Notion workspace to create a new integration associated with it.
:::

2. Enter a **Name** for your integration. Make sure you have selected the workspace containing your data to replicate from the **Associated workspace** dropdown menu, and click **Submit**.
3. In the navbar, select **Capabilities** and make sure to check the **Read content** checkbox to authorize Airbyte to read the content of your pages. You may also wish to check the **Read comments** box, as well as set a User capability to allow access to user information. For more details on the capabilities you can enable, please refer to the [Notion documentation on capabilities](https://developers.notion.com/reference/capabilities).

### Step 2: Set permissions and acquire authorization credentials

#### Access Token (Cloud and Open Source)
If you are authenticating via Access Token, you will need to manually set permissions for each page you want to share with Airbyte.

1. Navigate to the page(s) you want to share with Airbyte. Click the **•••** menu at the top right of the page, select **Add connections**, and choose the integration you created in Step 1. 
2. Once you have selected all the pages to share, you can find and copy the Access Token from the **Secrets** tab of your Notion integration's page. Then proceed to 
[setting up the connector in Airbyte](#step-2-set-up-the-notion-connector-in-airbyte).

<!-- env:oss -->
#### OAuth2.0 (Open Source only)
If you are authenticating via OAuth2.0 for Airbyte Open Source, you will need to make your integration public and acquire your Client ID, Client Secret and Access Token.

1. Navigate to the **Distribution** tab in your integration page, and toggle the switch to make the integration public.
2. Fill out the required fields in the **Organization information** and **OAuth Domain & URIs** section, then click **Submit**.
3. Navigate to the **Secrets** tab to find your Client ID and Client Secret.
4. You need to use your integration's authorization URL to set the necessary page permissions and send a request to obtain your Access Token. A thorough explanation of the necessary steps is provided in the [official Notion documentation](https://developers.notion.com/docs/authorization#public-integration-auth-flow-set-up). Once you have your Client ID, Client Secret and Access Token, you are ready to proceed to the next step.
<!-- /env:oss -->

### Step 3: Set up the Notion connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Notion** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Choose the method of authentication from the dropdown menu:

#### Authentication for Airbyte Cloud
- **OAuth2.0** (Recommended): Click **Authenticate your Notion account**. When the popup appears, click **Select pages**. Check the pages you want to give Airbyte access to, and click **Allow access**.
- **Access Token**: Copy and paste the Access Token found in the **Secrets** tab of your Notion integration's page.

#### Authentication for Airbyte Open Source
- **Access Token**: Copy and paste the Access Token found in the **Secrets** tab of your Notion integration's page.
- **OAuth2.0**: Copy and paste the Client ID, Client Secret and Access Token you acquired.

6. Enter the **Start Date** using the provided datepicker, or by programmatically entering a UTC date and time in the format: `YYYY-MM-DDTHH:mm:ss.SSSZ`. All data generated after this date will be replicated.
7. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Notion source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
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

| Version | Date       | Pull Request                                             | Subject                                                                      |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------|
| 1.1.1   | 2023-06-14 | [26535](https://github.com/airbytehq/airbyte/pull/26535) | Migrate from deprecated `authSpecification` to `advancedAuth`                |
| 1.1.0   | 2023-06-08 | [27170](https://github.com/airbytehq/airbyte/pull/27170) | Fix typo in `blocks` schema                                                  |
| 1.0.9   | 2023-06-08 | [27062](https://github.com/airbytehq/airbyte/pull/27062) | Skip streams with `invalid_start_cursor` error                               |
| 1.0.8   | 2023-06-07 | [27073](https://github.com/airbytehq/airbyte/pull/27073) | Add empty results handling for stream `Blocks`                               |
| 1.0.7   | 2023-06-06 | [27060](https://github.com/airbytehq/airbyte/pull/27060) | Add skipping 404 error in `Blocks` stream                                    |
| 1.0.6   | 2023-05-18 | [26286](https://github.com/airbytehq/airbyte/pull/26286) | Add `parent` field to `Blocks` stream                                        |
| 1.0.5   | 2023-05-01 | [25709](https://github.com/airbytehq/airbyte/pull/25709) | Fixed `ai_block is unsupported by API` issue, while fetching `Blocks` stream |
| 1.0.4   | 2023-04-11 | [25041](https://github.com/airbytehq/airbyte/pull/25041) | Improve error handling for API /search                                       |
| 1.0.3   | 2023-03-02 | [22931](https://github.com/airbytehq/airbyte/pull/22931) | Specified date formatting in specification                                   |
| 1.0.2   | 2023-02-24 | [23437](https://github.com/airbytehq/airbyte/pull/23437) | Add retry for 400 error (validation_error)                                   |
| 1.0.1   | 2023-01-27 | [22018](https://github.com/airbytehq/airbyte/pull/22018) | Set `AvailabilityStrategy` for streams explicitly to `None`                  |
| 1.0.0   | 2022-12-19 | [20639](https://github.com/airbytehq/airbyte/pull/20639) | Fix `Pages` stream schema                                                    |
| 0.1.10  | 2022-09-28 | [17298](https://github.com/airbytehq/airbyte/pull/17298) | Use "Retry-After" header for backoff                                         |
| 0.1.9   | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state                                                  |
| 0.1.8   | 2022-09-05 | [16272](https://github.com/airbytehq/airbyte/pull/16272) | Update spec description to include working timestamp example                 |
| 0.1.7   | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from shared schemas              |
| 0.1.6   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and spec                    |
| 0.1.5   | 2022-07-14 | [14706](https://github.com/airbytehq/airbyte/pull/14706) | Added OAuth2.0 authentication                                                |
| 0.1.4   | 2022-07-07 | [14505](https://github.com/airbytehq/airbyte/pull/14505) | Fixed bug when normalization didn't run through                              |
| 0.1.3   | 2022-04-22 | [11452](https://github.com/airbytehq/airbyte/pull/11452) | Use pagination for User stream                                               |
| 0.1.2   | 2022-01-11 | [9084](https://github.com/airbytehq/airbyte/pull/9084)   | Fix documentation URL                                                        |
| 0.1.1   | 2021-12-30 | [9207](https://github.com/airbytehq/airbyte/pull/9207)   | Update connector fields title/description                                    |
| 0.1.0   | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092)   | Initial Release                                                              |
