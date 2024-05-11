# Rocket.chat API

## Sync overview

This source can sync data from the [Rocket.chat API](https://developer.rocket.chat/reference/api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- teams
- rooms
- channels
- roles
- subscriptions
- users

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--_ | :--_ | :--\* |
| Full Refresh Sync | Yes | |
| Incremental Sync | No | |

### Performance considerations

Rocket.chat APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developer.rocket.chat/reference/api/rest-api/endpoints/other-important-endpoints/rate-limiter-endpoints)

## Getting started

### Requirements

You need to setup a personal access token within the Rocket.chat workspace, see [here](https://docs.rocket.chat/use-rocket.chat/user-guides/user-panel/my-account#personal-access-tokens) for step-by-step.

- token
- user_id
- endpoint

## Changelog

| Version | Date       | Pull Request                                              | Subject                                       |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------------------- |
| 0.1.0   | 2022-10-29 | [#18635](https://github.com/airbytehq/airbyte/pull/18635) | 🎉 New Source: Rocket.chat API [low-code CDK] |
