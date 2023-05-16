# Instagram

This page contains the setup guide and reference information for the Instagram source connector.

## Prerequisites

To set up the Instagram source connector, you will need the following:

* A [Meta for Developers account](https://developers.facebook.com) 
* An [Instagram business account](https://www.facebook.com/business/help/898752960195806) linked to your Facebook page
* The [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) associated with your Facebook app
* A [Facebook API access token](https://developers.facebook.com/docs/facebook-login/access-tokens/#usertokens)
* A [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762) to configure Instagram as a source in Airbyte

## Setting Up the Instagram Connector

Follow these steps to set up the Instagram connector in Airbyte:

### Step 1: Generate Instagram Access Tokens

1. Go to the [Facebook Developer dashboard](https://developers.facebook.com/).
2. Click on the "My Apps" button in the top-right corner and select the app you will be using for the Instagram source connector.
3. In your selected app's dashboard, navigate to "Instagram Basic Display" from the left-hand panel.
4. On the Instagram Basic Display page, click on the "Settings" tab.
5. Add a testing account or connect an existing Instagram business account.
6. In the "Instagram Accounts" section, click the "Create Account" button.
7. Follow the prompts to create an Instagram business account, or connect an existing one to your Facebook page.
8. On the "Instagram Basic Display" page, click on the "Generate Token" button to generate your access tokens.
9. In the popup window, select the permissions required for the connector from the following:
    * instagram_basic
    * instagram_manage_insights
    * pages_show_list
    * pages_read_engagement
    * Instagram Public Content Access
10. Click on the "Generate Token" button at the bottom of the popup window.

### Step 2: Setting up the Instagram Connector in Airbyte

1. Log in to your Airbyte account.
2. Click on the "+ New connection" button.
3. Select "Instagram" from the list of sources.
4. In the connection configuration form, enter a name for your source.
5. Enter the start date in YYYY-MM-DDTHH:mm:ssZ format (e.g., "2022-01-01T00:00:00Z"). This is the date from which you would like to replicate data for the "User Insights" stream. All data generated after this date will be replicated.
6. In the "Access Token" field, paste your Instagram access tokens from Step 1.
7. Click on the "Check connection" button to verify your connection.
8. Click on the "Create connection" button to save your connection.

## Supported Sync Modes

The Instagram source connector supports the following [sync modes](https://docs.airbyte.io/core-concepts/streams/connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.io/dbt/overwriting-data)
- [Full Refresh - Append](https://docs.airbyte.io/dbt/appending-data)
- [Incremental - Append](https://docs.airbyte.io/dbt/incremental-ingestion)
- [Incremental - Deduped History](https://docs.airbyte.io/dbt/incremental-ingestion)

Note that incremental sync modes are only available for the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights) stream.

## Supported Streams

The Instagram source connector supports the following streams:

- [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
    - [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
- [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
    - [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
- [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
    - [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

## Rate Limiting and Performance Considerations

Instagram limits the number of requests that can be made at a time. However, the Instagram connector is designed to handle rate limiting gracefully. For more information, see Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api).

## Data Type Map

Airbyte records must conform to the [Airbyte type](https://docs.airbyte.io/introduction/airbyte-specification#airbyte-data-types) system. This means that all sources must produce schemas and records within these types, and all destinations must handle records that conform to this type system.

| Integration Type | Airbyte Type |
| ---------------- | ------------ |
| string           | string       |
| number           | number       |
| array            | array        |
| object           | object       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                         |
| ------- | ---------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1.0.5   | 2023-03-28 | [24634](https://github.com/airbytehq/airbyte/pull/24634) | Add user-friendly message for no instagram_business_accounts case                                               |
| 1.0.4   | 2023-03-15 | [23671](https://github.com/airbytehq/airbyte/pull/23671) | Add info about main permissions in spec and doc links in error message to navigate user                         |
| 1.0.3   | 2023-03-14 | [24043](https://github.com/airbytehq/airbyte/pull/24043) | Do not emit incomplete records for `user_insights` stream                                                       |
| 1.0.2   | 2023-03-14 | [24042](https://github.com/airbytehq/airbyte/pull/24042) | Test publish flow                                                                                               |
| 1.0.1   | 2023-01-19 | [21602](https://github.com/airbytehq/airbyte/pull/21602) | Handle abnormally large state values                                                                            |
| 1.0.0   | 2022-09-23 | [17110](https://github.com/airbytehq/airbyte/pull/17110) | Remove custom read function and migrate to per-stream state                                                     |
| 0.1.11  | 2022-09-08 | [16428](https://github.com/airbytehq/airbyte/pull/16428) | Fix requests metrics for Reels media product type                                                               |
| 0.1.10  | 2022-09-05 | [16340](https://github.com/airbytehq/airbyte/pull/16340) | Update to latest version of the CDK (v0.1.81)                                                                   |
| 0.1.9   | 2021-09-30 | [6438](https://github.com/