# Napta 

## Sync overview

This source can sync data from [Napta](https://app.swaggerhub.com/apis/Napta/Napta/1.0.0). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams
Every streams except for `user_calendar` & `project_calendar`

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Create an API key

- Log in to Napta
- Contact the technical support (chat or mail)
- Ask for access to the API
- Write down your client id and client secret.

## Changelog

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.0   | 2023-17-03 | [23766](https://github.com/airbytehq/airbyte/pull/23766) | 🎉 New Source: Napta              |
