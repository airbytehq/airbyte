# Google PageSpeed Insights

This page guides you through the process of setting up the Google PageSpeed Insights source connector.

## Sync overview

## Prerequisites

- Your [Google PageSpeed `API Key`](https://developers.google.com/speed/docs/insights/v5/get-started#APIKey)

## Set up the Google PageSpeed Insights source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Google PageSpeed Insights** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key**, enter your [Google PageSpeed `API Key`](https://developers.google.com/speed/docs/insights/v5/get-started#APIKey).
6. For **URLs to analyse**, enter one or many URLs you want to create PageSpeed Insights for. Example: https://www.google.com.
7. For **Analyses Strategies**, enter either "desktop", "mobile" or both to define which Analyses strategy to use.
8. For **Lighthouse Categories**, select one or many of the provided options. Categories are also called "audits" in some of the [Google Lighthouse documentation](https://developer.chrome.com/docs/lighthouse/overview/).
9. Click **Set up source**.

> **IMPORTANT:** As of 2022-12-13, the PageSpeed Insights API - as well as this Airbyte Connector - allow to specify a URL with prefix "origin:" - like `origin:https://www.google.com`. This results in condensed, aggregated reports about the specified origin - see [this FAQ](https://developers.google.com/speed/docs/insights/faq). **However**: This option is not specified in any official documentation anymore, therefore it might be deprecated anytime soon!

## Supported sync modes

The Google PageSpeed Insights source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Supported Streams

The Google PageSpeed Insights source connector supports the following stream:

- [pagespeed](https://developers.google.com/speed/docs/insights/v5/get-started#cli): Full pagespeed report of the selected URLs, lighthouse categories and analyses strategies.

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

When using the connector without an API key, Google utilizes an undocumented, but strict rate limit - which also depends on how many global requests are currently sent to the PageSpeed API. The connector will retry, using an exponential backoff interval.

If the connector is used with an API key, Google allows for 25.000 queries per day and 240 queries per minute. Therefore, under normal usage, the connector should not trigger any rate limits.
[Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.13 | 2025-03-08 | [55322](https://github.com/airbytehq/airbyte/pull/55322) | Update dependencies |
| 0.2.12 | 2025-03-01 | [54925](https://github.com/airbytehq/airbyte/pull/54925) | Update dependencies |
| 0.2.11 | 2025-02-22 | [54400](https://github.com/airbytehq/airbyte/pull/54400) | Update dependencies |
| 0.2.10 | 2025-02-15 | [53729](https://github.com/airbytehq/airbyte/pull/53729) | Update dependencies |
| 0.2.9 | 2025-02-08 | [52367](https://github.com/airbytehq/airbyte/pull/52367) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51693](https://github.com/airbytehq/airbyte/pull/51693) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51118](https://github.com/airbytehq/airbyte/pull/51118) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50529](https://github.com/airbytehq/airbyte/pull/50529) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50030](https://github.com/airbytehq/airbyte/pull/50030) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49526](https://github.com/airbytehq/airbyte/pull/49526) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49177](https://github.com/airbytehq/airbyte/pull/49177) | Update dependencies |
| 0.2.2 | 2024-12-11 | [47793](https://github.com/airbytehq/airbyte/pull/47793) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44143](https://github.com/airbytehq/airbyte/pull/44143) | Refactor connector to manifest-only format |
| 0.1.17 | 2024-08-10 | [43617](https://github.com/airbytehq/airbyte/pull/43617) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43130](https://github.com/airbytehq/airbyte/pull/43130) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42770](https://github.com/airbytehq/airbyte/pull/42770) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42319](https://github.com/airbytehq/airbyte/pull/42319) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41706](https://github.com/airbytehq/airbyte/pull/41706) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41591](https://github.com/airbytehq/airbyte/pull/41591) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41155](https://github.com/airbytehq/airbyte/pull/41155) | Update dependencies |
| 0.1.10 | 2024-07-06 | [41011](https://github.com/airbytehq/airbyte/pull/41011) | Update dependencies |
| 0.1.9 | 2024-06-29 | [40439](https://github.com/airbytehq/airbyte/pull/40439) | Update dependencies |
| 0.1.8 | 2024-06-22 | [40104](https://github.com/airbytehq/airbyte/pull/40104) | Update dependencies |
| 0.1.7 | 2024-06-06 | [39272](https://github.com/airbytehq/airbyte/pull/39272) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.6 | 2024-05-21 | [38147](https://github.com/airbytehq/airbyte/pull/38147) | Make compatable with builder |
| 0.1.5 | 2024-04-19 | [37171](https://github.com/airbytehq/airbyte/pull/37171) | Updating to 0.80.0 CDK |
| 0.1.4 | 2024-04-18 | [37171](https://github.com/airbytehq/airbyte/pull/37171) | Manage dependencies with Poetry. |
| 0.1.3 | 2024-04-15 | [37171](https://github.com/airbytehq/airbyte/pull/37171) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2 | 2024-04-12 | [37171](https://github.com/airbytehq/airbyte/pull/37171) | schema descriptions |
| 0.1.1   | 2023-05-25 | [#22287](https://github.com/airbytehq/airbyte/pull/22287) | 🐛 Fix URL pattern regex                                                        |
| 0.1.0   | 2022-11-26 | [#19813](https://github.com/airbytehq/airbyte/pull/19813) | 🎉 New Source: Google PageSpeed Insights [low-code CDK]                         |

</details>
