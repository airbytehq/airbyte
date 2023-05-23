# Polygon Stock API

## Sync overview

This source can provide information about stock data available on 
[PolygonStocksApi](https://polygon.io). It currently only supports Full Refresh
syncs.

### Output schema

This source is capable of syncing the following streams:

* `stock_api`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                   |
|:------------------|:----------------------|:--------------------------------------------------------|
| Full Refresh Sync | Yes                   |                                                         |
| Incremental Sync  | No                    |                                                         |

### Performance considerations

Polygon Stocks API allows only 5 API Calls/Minute on the free plan. Use of this connector
may require a paid plan based on your requirements.

## Getting started

### Requirements

1. Obtain an API key from [PolygonStocksApi](https://polygon.io).
2. Find out the exchange symbol of the stock you're interested in, also known as the Ticker Symbol. This can be found using a search engine (e.g., the Ticker Symbol for Microsoft is MSFT).
3. Choose and verify other options for fetching stock details. [Polygon API Documentation](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to).

### Setup guide

The following fields are required for the connector to work:

- `apiKey`: Your Polygon Stocks API key. This can be obtained by signing up for an account on their [website](https://polygon.io/signup) and then accessing the API section under "Dashboard".
- `stocksTicker`: The Ticker Symbol of the `stock/equity` you want to access. For example, if you're interested in Microsoft's stock data, use "MSFT".
- `multiplier`: The size of the timespan multiplier. This is an integer value that represents your desired timespan increment, e.g., 1 or 2.
- `timespan`: The basic timespan unit for aggregating stock data. Supported options are "day", "hour", "minute", etc. For example, if you want daily stock data, use "day".
- `start_date`: The start of the aggregate time window. The format should be in YYYY-MM-DD format, e.g., "2020-10-14".
- `end_date`: The end of the aggregate time window. The format should be in YYYY-MM-DD format, e.g., "2020-11-14".

(Optional) Additional fields can also be provided:

- `adjusted`: Determines whether or not the results are adjusted for splits. By default, results are adjusted and set to "true". Set this to "false" to get results that are NOT adjusted for splits.
- `sort`: Sort the results by timestamp. "asc" will return results in ascending order (oldest at the top), "desc" will return results in descending order (newest at the top).
- `limit`: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000. Read more about how the limit is used to calculate aggregate results in their [blog post on Aggregate Data API Improvements](https://polygon.io/blog/aggs-api-updates/).

Once you have completed the fields in the Airbyte configuration form, click "Set up Source" to save your settings and begin syncing your stock data.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2023-02-13 | [22908](https://github.com/airbytehq/airbyte/pull/22908) | Specified date formatting in specificatition  |
| 0.1.0   | 2022-11-02 | [18842](https://github.com/airbytehq/airbyte/pull/18842) | New source |