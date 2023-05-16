# Aha API

API Documentation link [here](https://www.aha.io/api)

## Overview

The Aha API source supports full refresh syncs.

### Output schema

Two output streams are available from this source:

* [features](https://www.aha.io/api/resources/features/list_features).
* [products](https://www.aha.io/api/resources/products/list_products_in_the_account).

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Rate Limiting information is updated [here](https://www.aha.io/api#rate-limiting).

## Getting started

### Requirements

* Aha API Key.

### Configuration steps:

1. Log in to your Aha account.
2. Click on your profile image in the top right-hand corner of the screen and click on Account settings.
3. Click on the API Keys tab.
4. Click on the Add a new API Key button.
5. Enter a name for your API key and click on the Create API Key button.
6. Copy the generated API Key for use in Airbyte.
7. In Airbyte, go to the Aha connector configuration page.
8. Enter the Aha URL instance for your account in the URL field.
9. Paste the copied API Key into the API Bearer Token field.
10. Test the connection and save the configuration.

For more information on generating an API key, please see the [Aha API documentation](https://www.aha.io/api#authentication).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-02 | [18883](https://github.com/airbytehq/airbyte/pull/18893) | 🎉 New Source: Aha                              |