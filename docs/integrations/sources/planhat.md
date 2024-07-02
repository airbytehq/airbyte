# Planhat

## Sync overview

The Planhat API source supports Full Refresh only.

This source can sync data for the [general Planhat API](https://docs.planhat.com/#**planhat_models**ß)

### Output schema

This Source is capable of syncing the following core Streams:

- [companies](https://docs.planhat.com/#companies)
- [conversations](https://docs.planhat.com/#conversations)
- [custom_fields](https://docs.planhat.com/#custom_fields)
- [endusers](https://docs.planhat.com/#endusers)
- [invoices](https://docs.planhat.com/#invoices)
- [issues](https://docs.planhat.com/#issues)
- [licenses](https://docs.planhat.com/#licenses)
- [nps](https://docs.planhat.com/#nps)
- [opportunities](https://docs.planhat.com/#opportunities)
- [objectives](https://docs.planhat.com/#objectives)
- [sales](https://docs.planhat.com/#sales)
- [tasks](https://docs.planhat.com/#tasks)
- [tickets](https://docs.planhat.com/#tickets)
- [users](https://docs.planhat.com/#users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |

## Requirements

- **Planhat API token**. See the [Planhat API docs](https://docs.planhat.com/#authentication) for information on how to obtain the API token.

## Changelog

| Version | Date       | Pull Request                                             | Subject               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------- |
| 0.1.0   | 2024-01-11 | [34143](https://github.com/airbytehq/airbyte/pull/34143) | 🎉 New Source: Planhat |
