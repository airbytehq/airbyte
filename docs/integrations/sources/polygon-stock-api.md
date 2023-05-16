# Polygon Stock API

## Sync overview

This source can give information about stocks data available on [PolygonStocksApi](https://polygon.io). It currently only supports Full Refresh syncs.

### Output schema

This source is capable of syncing the following streams:

* `stock_api`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                   |
|:------------------|:----------------------|:--------------------------------------------------------|
| Full Refresh Sync | Yes                   |                                                         |
| Incremental Sync  | No                    |                                                         |

### Performance considerations

Polygon Stocks API allows only 5 API Calls/Minute on the free plan. Use of this connector may require a paid plan based upon your requirements.

## Getting started

### Configuration

The configuration is based on the provided Airbyte Connector Spec and some information from [PolygonStocksApi](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to). 

Please follow these steps to set up your polygon-stock-api source connector correctly:

1. Obtain an API key from [PolygonStocksApi](https://polygon.io). You can follow the instructions [here](https://polygon.io/dashboard/signup) to create an account and generate an API key.

2. Find the exchange symbol of the stock also known as Ticker Symbol of the stock you want to fetch. You can find this symbol by searching for the company name or ticker symbol on Google. For example, the exchange symbol for Microsoft is MSFT.

3. Choose and verify other options that you require for fetching your stock details. You can find all the options explained in detail [here](https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to).

### Connector configuration

Here are the required and optional fields for the polygon-stock-api source connector to work:

| Field       | Type    | Required? | Description                                                                                                     |
|:------------|:--------|:----------|:----------------------------------------------------------------------------------------------------------------|
| apiKey      | string  | Yes       | Your Polygon Stocks API key.                                                                                    |
| stocksTicker| string  | Yes       | The ticker symbol of the stock.                                                                                 |
| multiplier  | integer | Yes       | The size of the timespan multiplier.                                                                             |
| timespan    | string  | Yes       | The size of the time window.                                                                                     |
| from        | string  | Yes       | The start of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.    | 
| to          | string  | Yes       | The end of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.      |
| adjusted    | string  | No        | Determines whether or not the results are adjusted for splits. By default, results are adjusted and set to true.|
| sort        | string  | No        | Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top). |
| limit       | integer | No        | Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000.     |

Please follow these steps to set up the connector configuration correctly:

1. Enter your API key in the `apiKey` field.

2. Enter the ticker symbol of the stock you want to fetch in the `stocksTicker` field. 

3. Enter the size of the timespan multiplier in the `multiplier` field. 

4. Enter the size of the time window in the `timespan` field. 

5. Enter the start date of the aggregate time window in the `from` field. This can either be a date with the format `YYYY-MM-DD` or a millisecond timestamp.

6. Enter the end date of the aggregate time window in the `to` field. This can either be a date with the format `YYYY-MM-DD` or a millisecond timestamp.

7. If you don’t want the results of your API request to be adjusted for splits, change the `adjusted` field to `false`. Otherwise, leave the field as is. 

8. If you want to sort the results by timestamp in ascending or descending order, enter either `asc` or `desc` in the `sort` field.

9. If you want to limit the number of base aggregates queried to create the aggregate results, enter a value between 0 and 50,000 in the `limit` field. If not, leave the field as is.

At this point, you are ready to set up your polygon-stock-api source connector in Airbyte. You can now proceed with saving your configuration and testing your connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2023-02-13 | [22908](https://github.com/airbytehq/airbyte/pull/22908) | Specified date formatting in specificatition  |
| 0.1.0   | 2022-11-02 | [18842](https://github.com/airbytehq/airbyte/pull/18842) | New source |