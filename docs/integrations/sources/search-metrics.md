# SearchMetrics

## Overview

The SearchMetrics source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

Several output streams are available from this source:

* [Projects](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQwODQ5ODE-get-list-projects) \(Full table\)
* [BenchmarkRankingsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NDY-get-list-benchmark-rankings-s7) \(Full table\)
* [CompetitorRankingsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NDc-get-list-competitor-rankings-s7) \(Full table\)
* [DistributionKeywordsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NDg-get-list-distribution-keywords-s7) \(Full table\)
* [KeywordPotentialsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTA-get-list-keyword-potentials-s7) \(Full table\)
* [ListCompetitors](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQwODQ5OTI-get-list-competitors) \(Full table\)
* [ListCompetitorsRelevancy](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQxODQxNjU-get-list-competitors-relevancy) \(Full table\)
* [ListLosersS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTE-get-list-losers-s7) \(Full table\)
* [ListMarketShareS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTI-get-list-market-share-s7) \(Incremental\)
* [ListPositionSpreadHistoricS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTM-get-list-position-spread-historic-s7) \(Incremental\)
* [ListRankingsDomain](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQwODQ5OTg-get-list-rankings-domain) \(Full table\)
* [ListRankingsHistoricS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTY-get-list-rankings-historic-s7) \(Full table\)
* [ListSeoVisibilityCountry](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQyMjg4NDk-get-list-seo-visibility-country) \(Full table\)
* [ListSeoVisibilityHistoricS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTc-get-list-seo-visibility-historic-s7) \(Incremental\)
* [ListSerpSpreadS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTg-get-list-serp-spread-s7) \(Full table\)
* [ListWinnersS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NjQ-get-list-winners-s7) \(Full table\)
* [SeoVisibilityValueS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQyMzQzMjk-get-value-seo-visibility) \(Full table\)
* [SerpSpreadValueS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0Njc-get-value-serp-spread-s7) \(Full table\)
* [TagPotentialsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NTk-get-list-tag-potentials-s7) \(Full table\)
* [Tags](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjE4NzQ0ODMz-get-list-project-tags) \(Full table\)
* [UrlRankingsS7](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQzNjc0NjM-get-list-url-rankings-s7) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |


The SearchMetrics connector should not run into SearchMetrics API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* SearchMetrics Client Secret
* SearchMetrics API Key

### Setup guide

Please read [How to get your API Key and Client Secret](https://developer.searchmetrics.com/docs/apiv4-documentation/ZG9jOjQ2Nzk1-getting-started) .

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.1   | 2021-12-22 | [6992](https://github.com/airbytehq/airbyte/pull/6992) | Deleted windows in days from config |
| 0.1.0   | 2021-10-13 | [6992](https://github.com/airbytehq/airbyte/pull/6992) | Release SearchMetrics CDK Connector |
