# Polygon Stock API

## Sync overview

This source can give information about stocks data available on 
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
may require a paid plan based upon your requirements.

## Getting started

### Requirements

1. Obtain an API key from [PolygonStocksApi](https://polygon.io).
2. Find out the exchange symbol of the stock also known as Ticker Symbol of the stock you can google it out and find it (E.x. : Exchange symbol for Microsoft is MSFT)
3. Choose and verify other options you required for fetching the stock details. [here](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to).

### Setup guide

The following fields are required fields for the connector to work:
- `apiKey`: Your Polygon Stocks API key.
- `stocksTicker`: The ticker symbol of the `stock/equity`.
- `multiplier`: The size of the timespan multiplier.
- `timespan`: The 
- `from`: The start of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
- `to`: The end of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
- (optional) `adjusted`: determines whether or not the results are adjusted for splits. By default, results are adjusted and set to true. Set this to false to get results that are NOT adjusted for splits.
- (optional) `sort`: Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top).
- (optional) `limit`: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000. Read more about how limit is used to calculate aggregate results in our article on Aggregate Data API Improvements [Find-more](https://polygon.io/blog/aggs-api-updates/).





## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2023-02-13 | [22908](https://github.com/airbytehq/airbyte/pull/22908) | Specified date formatting in specificatition  |
| 0.1.0   | 2022-11-02 | [18842](https://github.com/airbytehq/airbyte/pull/18842) | New source |
