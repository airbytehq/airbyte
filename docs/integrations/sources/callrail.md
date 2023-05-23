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

To set up the CallRail source connector in Airbyte, you will need the following:

* Access to a CallRail account
* A CallRail API Token, which can be created and obtained by following the instructions outlined in the [CallRail API documentation](https://apidocs.callrail.com/#authentication)

### Connection steps

1. In the Airbyte UI, navigate to the CallRail configuration form.
2. Enter a nickname for the new connection.
3. Enter the `api_key` and `account_id` associated with your CallRail account. The `api_key` serves as the authentication token to access the CallRail account via API. The `account_id` can be found in the URL of your CallRail account dashboard.
4. Enter the start date that data should be synced from. The date should be in the format `YYYY-MM-DD`.
5. Click "Save" to save the changes to the configuration.

For detailed instructions on setting up your CallRail API token and finding your `account_id`, please refer to the [CallRail API documentation](https://apidocs.callrail.com/#authentication).

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |

Note: Do not change the Changelog. Do not change any Markdown tables. Only change content that includes obvious typos or is related how to fill out the configuration. Do not assume any images are available that are not in the original documentation.