# Tempo

## Overview

This Source uses the [REST API version 3](https://tempo-io.github.io/tempo-api-docs/) to sync Tempo data.

### Output schema

This connector outputs the following streams:

* Accounts
* Customers
* Worklogs
* Workload Schemes

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Getting started

### Requirements

* API Token

### Setup guide

Source Tempo is designed to interact with the data your permissions give you access to. To do so, you will need to generate a Tempo OAuth 2.0 token for an individual user.

Go to **Tempo &gt; Settings**, scroll down to **Data Access** and select **API integration**.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.6   | 2022-09-08 | [16361](https://github.com/airbytehq/airbyte/pull/16361) | Avoid infinite loop for non-paginated APIs |
| 0.2.4   | 2021-11-08 | [7649](https://github.com/airbytehq/airbyte/pull/7649) | Migrate to the CDK |

