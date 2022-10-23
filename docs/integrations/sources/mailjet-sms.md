# Mailjet - SMS API

## Sync overview

This source can sync data from the [Mailjet SMS API](https://dev.mailjet.com/sms). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* SMS

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://dev.mailjet.com/sms/reference/overview/rate-limits/)

## Getting started

### Requirements

* Mailjet Mail API_KEY (username)
* Mailjet Mail SECRET_KEY (password)