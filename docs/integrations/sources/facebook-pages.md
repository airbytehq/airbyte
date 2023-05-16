# Facebook Pages

This page contains the setup guide and reference information for the Facebook Pages API source connector.

## Prerequisites

To set up the Facebook Pages API source connector with Airbyte, you'll need to create your Facebook Application and use both long-lived Page access token and Facebook Page ID.

:::note
The Facebook Pages API source connector is currently only compatible with v15 of the Facebook Graph API.
:::

## Setup guide
### Step 1: Set up Facebook Pages

1. Create a Facebook Developer Account. Follow [these instructions](https://developers.facebook.com/async/registration/) to create one.
2. Create a [new Facebook App](https://developers.facebook.com/apps/). Choose "Company" as the purpose of the app. Fill out the remaining fields to create your app, then follow along with the "Connect a User Page" section.
3. Connect a User [Page](https://developers.facebook.com/tools/explorer/). Choose your app in the `Meta App` field. Choose your Page in the `User or Page` field. Add the following permissions:
    * pages_read_engagement
    * pages_read_user_content
    * pages_show_list
    * read_insights
4. Generate a [long-lived user access token](https://developers.facebook.com/docs/facebook-login/access-tokens/refreshing/) that includes the following scopes:
    * pages_read_engagement
    * pages_read_user_content
    * pages_show_list
    * read_insights
5. Generate a [long-lived page access token](https://developers.facebook.com/docs/pages/access-tokens#making-a-page-access-token-long-lived) for your Page.

### Step 2: Set up the Facebook Pages connector in Airbyte

1. In the Facebook Pages connector configuration screen of Airbyte, enter the name for the connector.
2. Enter both the long-lived page access token generated in Step 1 and the Page ID. If you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be `Test-1111111111`.

## Supported sync modes

The Facebook Pages API source connector supports the following [sync modes](https://docs.airbyte.io/cloud-core-concepts/connections#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.io/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.io/understanding-airbyte/connections/full-refresh-append)


## Supported Streams

The Facebook Pages API source connector supports the following streams:

| Stream | Description |
|:-------|:------------|
| Page | Returns data about a particular Facebook Page such as category, name, phone, and more. |
| Post | Returns data about a particular Facebook Page's posts. |
| Page Insights | Returns data about a particular Facebook Page's insights. |
| Post Insights | Returns data about a particular Facebook Page post's insights. |

## Data type mapping

The following table shows how Facebook data types are mapped to Airbyte data types:

| Facebook Type | Airbyte Type |
|:--------------|:-------------|
| `string`      | `string`     |
| `number`      | `number`     |
| `array`       | `array`      |
| `object`      | `object`     |

## Performance considerations

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting, follow the instructions in the Setup Guide above to access better rate limits.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) for more information on requesting a quota upgrade.