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

## Setup Guide

To set up the Polygon Stocks API source connector, you will need to provide the following information:

1. [Obtain your API key from Polygon.io](https://polygon.io/dashboard/signup)
2. Determine the stock ticker symbol (exchange symbol) for the stock you want to fetch data for. You can search for the stock ticker symbol using a search engine or financial news websites.
3. Choose any additional options you need for fetching stock details. More information on these options can be found in the [Polygon Documentation](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to).

### Required Fields

To configure the Polygon Stocks API source connector, you will need to input the following required fields:

- **apiKey**: Your Polygon Stocks API key. This can be found in your [Polygon dashboard](https://polygon.io/dashboard/api-keys/).
- **stocksTicker**: The stock ticker symbol (exchange symbol) of the stock you want to fetch data for (e.g., "MSFT" for Microsoft).
- **multiplier**: The size of the timespan multiplier. This will be an integer value, such as 1 or 2.
- **timespan**: The size of the time window. Possible values include: "minute", "hour", "day", "week", "month", "quarter", or "year".
- **start_date**: The start of the aggregate time window. This value should be a date in the format "YYYY-MM-DD" (e.g., "2022-01-01").
- **end_date**: The end of the aggregate time window. This value should be a date in the format "YYYY-MM-DD" (e.g., "2022-12-31").

### Optional Fields

The following fields are optional but can be provided to further refine the data fetched by the connector:

- **adjusted** (optional): Determines whether the results are adjusted for stock splits. By default, results are adjusted and set to "true". Set this value to "false" to get results that are NOT adjusted for stock splits.
- **sort** (optional): Sort the results by timestamp. Use "asc" to return results in ascending order (oldest at the top) or "desc" to return results in descending order (newest at the top).
- **limit** (optional): Limits the number of base aggregates queried to create the aggregate results. The maximum limit is 50,000, and the default limit is 5,000. Read more about how limit is used to calculate aggregate results in the [Polygon blog post on Aggregate Data API Improvements](https://polygon.io/blog/aggs-api-updates/).

With the above information, fill in the corresponding fields in the Polygon Stocks API source connector configuration form in Airbyte. After configuring the connector, proceed to create a new connection to start syncing data from the Polygon Stocks API.





## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2023-02-13 | [22908](https://github.com/airbytehq/airbyte/pull/22908) | Specified date formatting in specificatition  |
| 0.1.0   | 2022-11-02 | [18842](https://github.com/airbytehq/airbyte/pull/18842) | New source |
