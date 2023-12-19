# BambooHR

<HideInUI>

This page contains the setup guide and reference information for the [BambooHR](https://www.bamboohr.com/) source connector.

</HideInUI>

## Prerequisites

* BambooHR Account
* BambooHR [API key](https://documentation.bamboohr.com/docs)

## Setup Guide

## Step 1: Set up the BambooHR connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the BambooHR connector and select **BambooHR** from the Source type dropdown.
3. Enter your `subdomain`. If you access BambooHR at https://mycompany.bamboohr.com, then the subdomain is "mycompany".
4. Enter your `api_key`. To generate an API key, log in and click your name in the upper right-hand corner of any page to get to the user context menu. If you have sufficient administrator permissions, there will be an "API Keys" option in that menu to go to the page.
5. (Optional) Enter any `Custom Report Fields` as a comma-separated list of fields to include in your custom reports. Example: `firstName,lastName`. If none are listed, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned.
6. Toggle `Custom Reports Include Default Fields`. If true, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned. If false, then the values defined in `Custom Report Fields` will be returned.
7. Click **Set up source**

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte OSS:**

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `subdomain`. If you access BambooHR at https://mycompany.bamboohr.com, then the subdomain is "mycompany".
4. Enter your `api_key`. To generate an API key, log in and click your name in the upper right-hand corner of any page to get to the user context menu. If you have sufficient administrator permissions, there will be an "API Keys" option in that menu to go to the page.
5. (Optional) Enter any `Custom Report Fields` as a comma-separated list of fields to include in your custom reports. Example: `firstName,lastName`. If none are listed, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned.
6. Toggle `Custom Reports Include Default Fields`. If true, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned. If false, then the values defined in `Custom Report Fields` will be returned.
7. Click **Set up source**

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The BambooHR source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| SSL connection | Yes |
| Namespaces | No |


## Supported Streams

* [Custom Reports](https://documentation.bamboohr.com/reference/request-custom-report-1)

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about BambooHR connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

BambooHR has the [rate limits](https://documentation.bamboohr.com/docs/api-details), but the connector should not run into API limitations under normal usage.

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Troubleshooting

* Check out common troubleshooting issues for the BambooHR source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
|:--------| :--------- | :------------------------------------------------------  | :---------------------------------------- |
| 0.2.2   | 2022-09-16 | [17684](https://github.com/airbytehq/airbyte/pull/17684) | Fix custom field validation retrieve      |
| 0.2.1   | 2022-09-16 | [16826](https://github.com/airbytehq/airbyte/pull/16826) | Add custom fields validation during check |
| 0.2.0   | 2022-03-24 | [11326](https://github.com/airbytehq/airbyte/pull/11326) | Add support for Custom Reports endpoint   |
| 0.1.0   | 2021-08-27 | [5054](https://github.com/airbytehq/airbyte/pull/5054)   | Initial release with Employees API        |

</HideInUI>