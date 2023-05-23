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

1. Log in to your CallRail account.

2. Navigate to the [API Tokens page](https://www.callrail.com/settings/api-tokens/) by clicking on the "Settings" icon on the left sidebar, then click on "API Tokens" under the "Integrations" section.

3. If you don't have an existing API token, generate a new token by clicking the "New API Key" button. If prompted, grant the necessary permissions for the new token.

4. Copy the generated API token from the list.

5. Navigate to the [Account ID page](https://www.callrail.com/settings/account-id/) by clicking on the "Settings" icon again on the left sidebar, then click on "Account ID" under the "General" section.

6. Copy the Account ID displayed on the page.

7. In Airbyte's CallRail Source connector configuration form, enter the following information:

    - **api_key**: Paste the API token you copied in step 4.
    - **account_id**: Paste the Account ID you copied in step 6.
    - **start_date**: Enter the date in the format `YYYY-MM-DD` from which you want to start syncing data. For example, `2022-01-01`.

For more information on CallRail API tokens and permissions, refer to the [CallRail API documentation](https://apidocs.callrail.com/#introduction).

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |