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

* CallRail Account
* CallRail API Token

### How to set up the CallRail Source Connector in Airbyte

1. Log in to your CallRail account and go to the [API Tokens](https://app.callrail.com/settings/api) page.
2. Click on the "New Token" button. Enter a name for your token, and select the permissions you want to grant for this token.
3. Copy the newly generated API Token.
4. Log in to Airbyte and select "CallRail" from the list of available sources.
5. Paste the API token into the "API Key" field.
6. Find your Account ID in CallRail. To do this, go to the "Settings" tab and select "General" from the dropdown.
7. Copy the "Account ID" field value.
8. Return to the Airbyte connector configuration page and enter the copied Account ID into the "Account ID" field. 
9. Determine the date from which you want to start obtaining data. Copy the date (in the format: YYYY-MM-DD).
10. Return to the Airbyte connector configuration page and enter the copied date into the "Start Date" field.
11. Click "Test Connection" to ensure the configuration is valid.
12. If the connection tests successfully, click "Create Connection" to save the configuration.

Refer to the [CallRail API Documentation](https://apidocs.callrail.com/) for more information on how to use the API. 

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |