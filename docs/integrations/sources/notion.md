# Notion

Notion is a productivity and project management software. It was designed to help organizations coordinate deadlines, objectives, and assignments.

## Prerequisites
* Created Notion account with integration on [my integrations](https://www.notion.so/my-integrations) page. 

## Airbyte Open Source
* Start Date
* Token (received when integration was created). 

## Airbyte Cloud
* Start Date
* Client ID (received when integration was created).
* Client Secret (received when integration was created).

## Setup guide
### Step 1: Set up Notion

1. Create account on Notion by following link [signup](https://www.notion.so/signup)
2. Login to your Notion account and go to [my integrations](https://www.notion.so/my-integrations) page.
3. Create a **new integration**. Make sure to check the `Read content` capability.
4. Check the appropriate user capability depending on your use case.
5. Check the settings **Integration type** and select **Public** (OAuth2.0 authentication) or **Internal** (Token authorization) integration
6. If you select Public integration you need to go to the opened section **OAuth Domain & URIs** and fill all fields of form you've received.
7. Click `Submit`.
8. Copy the **access_token** or **client_id** and **client_secret** from the next screen depending on selected authentication method.

## Step 2: Set up the Notion connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Notion** from the Source type dropdown and enter a name for this connector.
4. Add required Start date
5. Choose the method of authentication
6. If you select Token authentication - fill the field **token** with **access_token** in setup Notion step (8)
7. If you select OAuth2.0 authorization - Click `Authenticate your Notion account`.
8. Log in and Authorize to the Notion account
10. Click `Set up source`.

### For Airbyte Open Source:
1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the Set up the source page, enter the name for the connector and select **Notion** from the Source type dropdown. 
4. Add required Start date
5. Copy and paste values from setup Notion step (8):
      1) **client_id**
      2) **client_secret**
7. Click `Set up source`.

## Supported sync modes

The Notion source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental (partially)

## Supported Streams

* [blocks](https://developers.notion.com/reference/retrieve-a-block)
* [databases](https://developers.notion.com/reference/retrieve-a-database)
* [pages](https://developers.notion.com/reference/retrieve-a-page)
* [users](https://developers.notion.com/reference/retrieve-a-get-users) (this stream is not support **Incremental** - _Append Sync_ mode)

For more information, see the [Notion API](https://developers.notion.com/reference/intro).

## Performance considerations

The connector is restricted by normal Notion [rate limits and size limits](https://developers.notion.com/reference/errors#request-limits).

The Notion connector should not run into Notion API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------|
| 0.1.7   | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from shared schemas |
| 0.1.6   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas and spec |
| 0.1.5   | 2022-07-14 | [14706](https://github.com/airbytehq/airbyte/pull/14706) | Added OAuth2.0 authentication                             |
| 0.1.4   | 2022-07-07 | [14505](https://github.com/airbytehq/airbyte/pull/14505) | Fixed bug when normalization didn't run through           |
| 0.1.3   | 2022-04-22 | [11452](https://github.com/airbytehq/airbyte/pull/11452) | Use pagination for User stream                            |
| 0.1.2   | 2022-01-11 | [9084](https://github.com/airbytehq/airbyte/pull/9084)   | Fix documentation URL                                     |
| 0.1.1   | 2021-12-30 | [9207](https://github.com/airbytehq/airbyte/pull/9207)   | Update connector fields title/description                 |
| 0.1.0   | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092)   | Initial Release                                           |
