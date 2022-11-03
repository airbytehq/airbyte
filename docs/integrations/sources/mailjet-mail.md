# Mailjet - Mail API

## Sync overview

This source can sync data from the [Mailjet Mail API](https://dev.mailjet.com/email). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* contact list
* contacts
* messages
* campaigns
* stats

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://dev.mailjet.com/email/reference/overview/rate-limits/)

## Getting started

### Requirements

* Mailjet Mail API_KEY
* Mailjet Mail SECRET_KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-26 | [#18332](https://github.com/airbytehq/airbyte/pull/18332) | 🎉 New Source: Mailjet Mail API [low-code CDK] |