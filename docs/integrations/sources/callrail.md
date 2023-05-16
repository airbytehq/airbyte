# CallRail

## Overview

The CallRail source connector supports Full Refresh and Incremental syncs for the following core Streams:

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

## Getting Started

### Requirements

Before setting up the CallRail source connector, make sure the following requirements are met:

* A CallRail account.
* A CallRail API Token.

### Configuration

1. After selecting CallRail as the source connector in Airbyte, provide the following details from your CallRail account to configure the connector:

   * `api_key:` The API access key for your CallRail account. You can generate this key by following the instructions provided in CallRail's ["API Documentation"](https://apidocs.callrail.com/#getting-started).
   * `account_id:` Your CallRail account ID. You can obtain this ID from your CallRail dashboard by navigating to __Settings__ > __Account__ > __Account ID__.
   * `start_date:` The date where data syncing starts. This should be in the format `yyyy-mm-dd`.

2. Once you've entered all required details, click the "Check Connection" button. If the details provided are correct, you will receive a confirmation message and will be redirected to the "Create Flow" screen.

   > Note: If you receive an error message, please double-check that the API key, account ID, and start date are correct.

3. On the "Create Flow" screen, select the streams you want to replicate and follow the prompts to set your destination.

4. Give your flow a name and click "Create" to start the first sync. You can monitor the sync's progress on the "Connections" screen.