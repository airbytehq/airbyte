# Bamboo HR

## Overview

The BambooHr source supports Full Refresh sync. You can choose if this connector will overwrite the old records or duplicate old ones.

### Output schema

This connector outputs the following stream:

* [Custom Reports](https://documentation.bamboohr.com/reference/request-custom-report-1)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

BambooHR has the [rate limits](https://documentation.bamboohr.com/docs/api-details), but the connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* BambooHr Account
* BambooHr [Api key](https://documentation.bamboohr.com/docs)

# Bamboo HR

This page contains the setup guide and reference information for the Bamboo HR source connector.

## Prerequisites

* BambooHr Account
* BambooHr [Api key](https://documentation.bamboohr.com/docs)

## Setup guide
## Step 1: Set up the Bamboo HR connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Bamboo HR connector and select **Bamboo HR** from the Source type dropdown.
3. Enter your `subdomain`
4. Enter your `api_key`
5. Enter your `custom_reports_fields` if need
6. Choose `custom_reports_include_default_fields` flag value
7. Click **Set up source**

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `subdomain`
4. Enter your `api_key`
5. Enter your `custom_reports_fields` if need
6. Choose `custom_reports_include_default_fields` flag value
7. Click **Set up source**

## Supported sync modes

The Bamboo HR source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| SSL connection | Yes |
| Namespaces | No |


## Supported Streams

* [Custom Reports](https://documentation.bamboohr.com/reference/request-custom-report-1)

## Performance considerations

BambooHR has the [rate limits](https://documentation.bamboohr.com/docs/api-details), but the connector should not run into API limitations under normal usage. 
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
|:--------| :--------- | :------------------------------------------------------  | :---------------------------------------- |
| 0.2.2   | 2022-09-16 | [17684](https://github.com/airbytehq/airbyte/pull/17684) | Fix custom field validation retrieve      |
| 0.2.1   | 2022-09-16 | [16826](https://github.com/airbytehq/airbyte/pull/16826) | Add custom fields validation during check |
| 0.2.0   | 2022-03-24 | [11326](https://github.com/airbytehq/airbyte/pull/11326) | Add support for Custom Reports endpoint   |
| 0.1.0   | 2021-08-27 | [5054](https://github.com/airbytehq/airbyte/pull/5054)   | Initial release with Employees API        |
