# Polygon Stock API

## Sync overview

This source can provide information about available stocks data on the [PolygonStocksApi](https://polygon.io). It currently only supports Full Refresh syncs.

### Output schema

This source is capable of syncing the following stream:

* `stock_api`

### Features

| Feature | Supported? (Yes/No) | Notes |
| :------ | :------------------ | :---- |
| Full Refresh Sync | Yes |      |
| Incremental Sync | No |      |

### Performance considerations

Polygon Stocks API allows only 5 API Calls/Minute on the free plan. Use of this connector may require a paid plan based on your requirements.

## Getting started

### Requirements

Before you start, you need to have a Polygon Stocks API account. If you don't already have one, please sign up for a free account [here](https://polygon.io/dashboard/signup).

### Setup guide

Follow the steps below to set up the Polygon Stock API connector.

1. Obtain an API key from [PolygonStocksApi](https://polygon.io/dashboard/api-keys).
2. Go to the [Polygon Stocks API documentation](https://polygon.io/docs/), find the ticker symbol you want to get data for, and make a note of it.
3. Choose the options you require for fetching the stock details from [here](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to).
4. Enter the following required fields in the connector setup form:
  * `apiKey`: Your Polygon Stocks API key.
  * `stocksTicker`: The ticker symbol of the stock/equity you want to fetch data for.
  * `multiplier`: The size of the timespan multiplier.
  * `timespan`: The size of the time window.
  * `start_date`: The beginning date for the aggregate window in the format YYYY-MM-DD or a millisecond timestamp.
  * `end_date`: The target date for the aggregate window in the format YYYY-MM-DD or a millisecond timestamp.

The following optional fields can also be entered:
  * `adjusted`: determines whether or not the results are adjusted for splits. By default, results are adjusted and set to true. Set this to false to get results that are NOT adjusted for splits.
  * `sort`: Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top).
  * `limit`: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000. Read more about how limit is used to calculate aggregate results in our article on Aggregate Data API Improvements [Find-more](https://polygon.io/blog/aggs-api-updates/).

You can now test the connection and save it.

**Note:** If you encounter any issues while setting up the connector, please refer to the [Polygon Stock API documentation](https://polygon.io/docs/) or reach out to their support team.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2023-02-13 | [22908](https://github.com/airbytehq/airbyte/pull/22908) | Specified date formatting in specification  |
| 0.1.0   | 2022-11-02 | [18842](https://github.com/airbytehq/airbyte/pull/18842) | New source |