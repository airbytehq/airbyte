# Twitter

This page contains the setup guide and reference information for the Twitter source connector.

## Prerequisites

To set up the Twitter source connector, you'll need the [App only Bearer Token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens).

## Set up the Twitter connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Twitter** from the Source type dropdown.
4. Enter the name for the Twitter connector.
5. For **Access Token**, enter the [App only Bearer Token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens).
6. For **Search Query**, enter the query for matching Tweets. You can learn how to build this query by reading [build a query guide](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query).
7. For **Start Date (Optional)**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The start date for retrieving tweets cannot be more than 7 days in the past.
8. For **End Date (Optional)**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The end date for retrieving tweets must be a minimum of 10 seconds prior to the request time.
9. Click **Set up source**.

## Supported sync modes

The Twitter source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

- [Tweets](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)

## Performance considerations

Rate limiting is mentioned in the API [documentation](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.1.4 | 2024-06-06 | [39154](https://github.com/airbytehq/airbyte/pull/39154) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-05-21 | [38525](https://github.com/airbytehq/airbyte/pull/38525) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-03-06 | [23749](https://github.com/airbytehq/airbyte/pull/23749) | Spec and docs are improved for beta certification |
| 0.1.1 | 2023-03-03 | [23661](https://github.com/airbytehq/airbyte/pull/23661) | Incremental added for the "tweets" stream |
| 0.1.0   | 2022-11-01 | [18883](https://github.com/airbytehq/airbyte/pull/18858) | 🎉 New Source: Twitter                            |

</details>
