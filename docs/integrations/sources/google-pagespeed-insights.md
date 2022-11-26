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
6. For **URL to analyse**, enter the URL you want to create PageSpeed Insights for. Example: https://www.google.com
7. Click **Set up source**.

## Supported sync modes

The Google PageSpeed Insights source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Supported Streams

The Google PageSpeed Insights source connector supports the following streams:
- [pagespeed](https://developers.google.com/speed/docs/insights/v5/get-started#cli): Full pagespeed report of the url entered. More detailed, but only for the specified url.
- [origin_pagespeed](https://developers.google.com/speed/docs/insights/faq): Aggregated value for all the pages and subpages of a specific url. Less detailed but accounts for all the subpages as well.

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Google utilizes an undocumented rate limit which - under normal use - should not be triggered, even with huge datasets.
[Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-11-29 | [#18875](https://github.com/airbytehq/airbyte/pull/18875) | 🎉 New Source: Google PageSpeed Insights [low-code CDK] |
