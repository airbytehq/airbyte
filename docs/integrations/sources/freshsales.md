# Freshsales

This page contains the setup guide and reference information for the Freshsales source connector.

## Prerequisites

* Freshsales Account
* Freshsales API Key
* Freshsales Domain Name

Please read [How to find your API key](https://crmsupport.freshworks.com/support/solutions/articles/50000002503-how-to-find-my-api-key-).

## Setup guide

## Step 1: Set up the Freshsales connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. Set the name for your source
4. Enter your `Domain Name`
5. Enter your `API Key` obtained from [these steps](https://crmsupport.freshworks.com/support/solutions/articles/50000002503-how-to-find-my-api-key-)
6. Click **Set up source**


### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. Set the name for your source
4. Enter your `Domain Name`
5. Enter your `API Key` obtained from [these steps](https://crmsupport.freshworks.com/support/solutions/articles/50000002503-how-to-find-my-api-key-)
6. Click **Set up source**


## Supported sync modes

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |


## Supported Streams

Several output streams are available from this source:

* [Contacts](https://developers.freshworks.com/crm/api/#contacts)
* [Accounts](https://developers.freshworks.com/crm/api/#accounts)
* [Open Deals](https://developers.freshworks.com/crm/api/#deals)
* [Won Deals](https://developers.freshworks.com/crm/api/#deals)
* [Lost Deals](https://developers.freshworks.com/crm/api/#deals)
* [Open Tasks](https://developers.freshworks.com/crm/api/#tasks)
* [Completed Tasks](https://developers.freshworks.com/crm/api/#tasks)
* [Past appointments](https://developers.freshworks.com/crm/api/#appointments)
* [Upcoming appointments](https://developers.freshworks.com/crm/api/#appointments)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Performance considerations

The Freshsales connector should not run into Freshsales API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.


## Changelog

| Version | Date       | Pull Request                                             | Subject                         |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------|
| 0.1.4   | 2023-03-23 | [24396](https://github.com/airbytehq/airbyte/pull/24396) | Certify to Beta |
| 0.1.3   | 2023-03-16 | [24155](https://github.com/airbytehq/airbyte/pull/24155) | Set `additionalProperties` to `True` in `spec` to support BC |
| 0.1.2   | 2022-07-14 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Tune the `get_view_id` function |
| 0.1.1   | 2021-12-24 | [9101](https://github.com/airbytehq/airbyte/pull/9101)   | Update fields and descriptions  |
| 0.1.0   | 2021-11-03 | [6963](https://github.com/airbytehq/airbyte/pull/6963)   | 🎉 New Source: Freshsales       |
