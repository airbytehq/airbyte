# CallRail

## Overview

The CallRail source supports Full Refresh and Incremental syncs of calls, companies, text messages, and users.

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

### Configuration

1. Log in to your CallRail account.
2. Navigate to your Account Dashboard
3. Copy the **API Secret Key** from the bottom of the screen.
4. In Airbyte, fill out the connection screen for CallRail with the following information:

    * `account_id` (string, required): ID of the CallRail account you want to connect to.
    * `api_key` (string, required): API secret key for the CallRail account.
    * `start_date` (string, required): Start getting data from that date. Must be in the format of `YYYY-MM-DD`.

5. Test the connection to make sure it is successful.

For more information on connecting CallRail with Airbyte, refer to the [CallRail API documentation](https://apidocs.callrail.com/) and the [Airbyte Connector documentation](https://docs.airbyte.io/integrations/sources/callrail).

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |