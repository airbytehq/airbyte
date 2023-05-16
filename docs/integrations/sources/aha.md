# Aha API

API Documentation link [here](https://www.aha.io/api)

## Overview

The Aha API source supports full refresh syncs.

### Output schema

Two output streams are available from this source:

- [features](https://www.aha.io/api/resources/features/list_features).
- [products](https://www.aha.io/api/resources/products/list_products_in_the_account).

### Features

| Feature | Supported? | |:------------------|:-----------| | Full Refresh Sync | Yes | | Incremental Sync | No |

### Performance considerations

Rate Limiting information is updated [here](https://www.aha.io/api#rate-limiting).

## Getting started

### Requirements

- Aha API Key.

### Connect using `API Key`

To connect to Aha API source, you need an Aha API Key. Here is how to get one:

1. Log in to your Aha account.
1. Click on your name in the top right corner.
1. Select "Account Settings".
1. Click on "API Keys" in the left sidebar.
1. Click on "Create API Key".
1. Give the API Key a name and click on "Create".

### Configure Aha Connector in Airbyte

To configure the Aha Connector in Airbyte, you need to provide the following information:

- API Key
- URL

Here are the steps to configure the Aha Connector in Airbyte:

1. Go to the Airbyte dashboard.
1. Click on "Create a Connection".
1. Select "Aha API" from the list of sources.
1. In the form that appears, enter your API Key and URL. The API Key can be copied from the Aha website and the URL is
   the hostname you use to access Aha. The URL should be in the following format: https://\<subdomain>.aha.io.
1. Click "Check connection" to verify your input information.
1. Click "Create" to save the Aha connection in Airbyte.

## Changelog

| Version | Date | Pull Request | Subject |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0 | 2022-11-02 | [18883](https://github.com/airbytehq/airbyte/pull/18893) | 🎉 New Source: Aha |
