# Google PageSpeed Insights

This page guides you through the process of setting up the Google PageSpeed Insights source connector.

## Sync overview

## Prerequisites
- Your [Google PageSpeed `API Key`](https://developers.google.com/speed/docs/insights/v5/get-started#APIKey)

## Set up the Google PageSpeed Insights source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google PageSpeed Insights** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key**, enter your [Google PageSpeed `API Key`](https://developers.google.com/speed/docs/insights/v5/get-started#APIKey).
6. For **URLs to analyse**, enter one or many URLs you want to create PageSpeed Insights for. Example: https://www.google.com.
7. For **Analyses Strategies**, enter either "desktop", "mobile" or both to define which Analyses strategy to use.
8. For **Lighthouse Categories**, select one or many of the provided options. Categories are also called "audits" in some of the [Google Lighthouse documentation](https://developer.chrome.com/docs/lighthouse/overview/).
9. Click **Set up source**.

> **IMPORTANT:** As of 2022-12-13, the PageSpeed Insights API - as well as this Airbyte Connector - allow to specify a URL with prefix "origin:" - like ``origin:https://www.google.com``. This results in condensed, aggregated reports about the specified origin - see [this FAQ](https://developers.google.com/speed/docs/insights/faq). **However**: This option is not specified in any official documentation anymore, therefore it might be deprecated anytime soon!

## Supported sync modes

The Google PageSpeed Insights source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Supported Streams

The Google PageSpeed Insights source connector supports the following stream:

- [pagespeed](https://developers.google.com/speed/docs/insights/v5/get-started#cli): Full pagespeed report of the selected URLs, lighthouse categories and analyses strategies.
### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

When using the connector without an API key, Google utilizes an undocumented, but strict rate limit - which also depends on how many global requests are currently sent to the PageSpeed API. The connector will retry, using an exponential backoff interval.

If the connector is used with an API key, Google allows for 25.000 queries per day and 240 queries per minute. Therefore, under normal usage, the connector should not trigger any rate limits.
[Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-11-26 | [#19813](https://github.com/airbytehq/airbyte/pull/19813) | 🎉 New Source: Google PageSpeed Insights [low-code CDK] |
