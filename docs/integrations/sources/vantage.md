# Vantage API

## Sync overview

This source can sync data from the [Vantage API](https://vantage.readme.io/reference/general). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* Providers: Providers are the highest level API Primitive. A Provider represents either cloud infrastructure provider or a cloud service provider. Some examples of Providers include AWS, GCP or Azure. Providers offer many Services, which is documented below.
* Services: Services are what Providers offer to their customers. A Service is always tied to a Provider. Some examples of Services are EC2 or S3 from a Provider of AWS. A Service has one or more Products offered, which is documented below.
* Products: Products are what Services ultimately price on. Using the example of a Provider of 'AWS' and a Service of 'EC2', Products would be the individual EC2 Instance Types available such as 'm5d.16xlarge' or 'c5.xlarge'. A Product has one or more Prices, which is documented below.
* Reports

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Vantage APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://vantage.readme.io/reference/rate-limiting)

## Getting started

### Requirements

* Vantage Access token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18665](https://github.com/airbytehq/airbyte/pull/18665) | 🎉 New Source: Vantage API [low-code CDK] |