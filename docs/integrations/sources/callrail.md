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

### Setup Instructions

Follow these steps to find the necessary information in the CallRail interface for setting up the Airbyte CallRail Source connector:

1. Log in to your [CallRail account](https://app.callrail.com/).
2. Click on your profile icon located in the upper right corner of the screen.
3. From the dropdown menu, select *Account Settings*.
4. On the left navigation panel, click on *API Settings* under the *Developers* section.
5. Here, you can find your Account ID and generate an API Token if you haven't already. If you've generated a token previously, click on *Reveal Token* to view it. Make sure you store this token securely as it cannot be retrieved again once hidden.
6. Now, navigate to the Airbyte CallRail Source connector configuration form and fill in the following details:
    * **API Key**: Enter the API Token you found in Step 5.
    * **Account ID**: Enter the Account ID you found in Step 5.
    * **Start Date**: Specify the Start Date, in format YYYY-MM-DD, from which you want to retrieve data.
7. Once you've provided the necessary information, click on validate configuration and then click on "Set Up Source" on the right lower corner of the screen.

For more information about the CallRail API, refer to the [CallRail API documentation](https://apidocs.callrail.com/).

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |