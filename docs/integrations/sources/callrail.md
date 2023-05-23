# CallRail

## Overview

The CallRail source supports Full Refresh and Incremental syncs. 

### Output schema

This Source is capable of syncing the following core Streams:

* [Calls](https://apidocs.callrail.com/#calls)
* [Companies](https://apidocs.callrail.com/#companies)
* [Text Messages](https://apidocs.callrail.com/#text-messages)
* [Users](https://apidocs.callrail.com/#users)


### Features

| Feature | Supported? |
| :--- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection | No         |
| Namespaces | No         |

## Getting started

### Requirements

* CallRail Account with API acces
* CallRail API Token
* Airbyte Account

### Configuration

To set up the CallRail connector in Airbyte, you will need to follow these steps:

1. Select CallRail as the source you want to set up and click "Continue".
2. Enter a nickname for your connector, which can be any name of your choosing.
3. Enter your **CallRail API Token** and **Account ID** in the respective fields. If you don't have an API Token, follow the instructions in this [CallRail Documentation](https://apidocs.callrail.com/v3/#getting-started).
4. Enter the date from when you want to start getting data in `YYYY-MM-DD` format in the `start_date` field.
5. Click "Test Connection" to verify that the credentials and settings are correct.
6. If the test is successful, click "Create Connection" to save the configuration.

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |

For more information on the CallRail API, check out their [API Documentation](https://apidocs.callrail.com/).