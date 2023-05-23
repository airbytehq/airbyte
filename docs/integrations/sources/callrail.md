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

### Obtaining the API Token

1. Sign in to your [CallRail dashboard](https://callrail.com/login).
2. Click on your profile avatar in the top-right corner and select "Account Center."
3. In the "Account Center," click on the "My Profile" tab.
4. Under the "API Tokens" section, you will find your API Key. If you do not have an API Key, click "Create API Token" to generate a new one.

### Obtaining the Account ID

1. Once you are signed in to your [CallRail dashboard](https://callrail.com/login), click on the "Reports" tab.
2. In the "Reports Overview" page, look at the URL in the address bar. You will see a number in the URL after "/a/", which is your Account ID.

### Configuration

1. **API Key:** Enter the API Key that you obtained from your CallRail dashboard in the "API Key" field.
2. **Account ID:** Enter the Account ID obtained from the CallRail dashboard in the "Account ID" field.
3. **Start Date:** Enter the start date from which you want to fetch the data in the "Start Date" field. The date must be in the format `YYYY-MM-DD`.

Now that you have provided the required information, you can proceed with the CallRail Source connector in Airbyte.

For more details, you can refer to the [CallRail API documentation](https://apidocs.callrail.com/).

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |