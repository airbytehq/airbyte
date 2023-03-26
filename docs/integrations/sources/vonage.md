# Vonage

## Sync overview

This source can sync data from the [Vonage API](https://developer.vonage.com/). this connector only supports full refresh and incremental syncs. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* [Reports](https://developer.vonage.com/en/api/reports)

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |

### Performance considerations

Vonage APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 403 HTTP error code. See [here](https://developer.vonage.com/en/api-errors/reports#rate-limit)

## Getting started

### Requirements

* Vonage API Key
* Vonage API Secret
* Vonage Account ID (same as *API Key*)

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2023-03-28 | [#24551](https://github.com/airbytehq/airbyte/pull/24551) | 🎉 New Source: Vonage API [low-code CDK] |
