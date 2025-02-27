# BambooHR

<HideInUI>

This page contains the setup guide and reference information for the [BambooHR](https://www.bamboohr.com/) source connector.

</HideInUI>

## Prerequisites

- BambooHR Account
- BambooHR [API key](https://documentation.bamboohr.com/docs)

## Setup Guide

## Step 1: Set up the BambooHR connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the BambooHR connector and select **BambooHR** from the Source type dropdown.
4. Enter your `subdomain`. If you access BambooHR at https://mycompany.bamboohr.com, then the subdomain is "mycompany".
5. Enter your `api_key`. To generate an API key, log in and click your name in the upper right-hand corner of any page to get to the user context menu. If you have sufficient administrator permissions, there will be an "API Keys" option in that menu to go to the page.
6. (Optional) Enter any `Custom Report Fields` as a comma-separated list of fields to include in your custom reports. Example: `firstName,lastName`. If none are listed, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned.
7. (Optional) Enter a `Start date` to define the start period for getting data for TimeOff Requests. The default start_date will be 30 days from today's date. 
8. Toggle `Custom Reports Include Default Fields`. If true, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned. If false, then the values defined in `Custom Report Fields` will be returned.
9. Click **Set up source**

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte OSS:**

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `subdomain`. If you access BambooHR at https://mycompany.bamboohr.com, then the subdomain is "mycompany".
4. Enter your `api_key`. To generate an API key, log in and click your name in the upper right-hand corner of any page to get to the user context menu. If you have sufficient administrator permissions, there will be an "API Keys" option in that menu to go to the page.
5. (Optional) Enter any `Custom Report Fields` as a comma-separated list of fields to include in your custom reports. Example: `firstName,lastName`. If none are listed, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned.
6. (Optional) Enter a `Start date` to define the start period for getting data for TimeOff Requests. The default start_date will be 30 days from today's date. 
7. Toggle `Custom Reports Include Default Fields`. If true, then the [default fields](https://documentation.bamboohr.com/docs/list-of-field-names) will be returned. If false, then the values defined in `Custom Report Fields` will be returned.
8. Click **Set up source**

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The BambooHR source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| SSL connection            | Yes        |
| Namespaces                | No         |

## Supported Streams

- [Custom Reports](https://documentation.bamboohr.com/reference/request-custom-report-1)

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

- Check out common troubleshooting issues for the BambooHR source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.6.2 | 2025-02-22 | [54238](https://github.com/airbytehq/airbyte/pull/54238) | Update dependencies |
| 0.6.1 | 2025-02-15 | [53873](https://github.com/airbytehq/airbyte/pull/53873) | Update dependencies |
| 0.6.0 | 2024-12-02 | [48759](https://github.com/airbytehq/airbyte/pull/48759) | Fix incremental for TimeOff Requests stream |
| 0.5.9 | 2025-02-08 | [53441](https://github.com/airbytehq/airbyte/pull/53441) | Update dependencies |
| 0.5.8 | 2025-02-01 | [52909](https://github.com/airbytehq/airbyte/pull/52909) | Update dependencies |
| 0.5.7 | 2025-01-25 | [52201](https://github.com/airbytehq/airbyte/pull/52201) | Update dependencies |
| 0.5.6 | 2025-01-18 | [51771](https://github.com/airbytehq/airbyte/pull/51771) | Update dependencies |
| 0.5.5 | 2025-01-11 | [51263](https://github.com/airbytehq/airbyte/pull/51263) | Update dependencies |
| 0.5.4 | 2024-12-28 | [50440](https://github.com/airbytehq/airbyte/pull/50440) | Update dependencies |
| 0.5.3 | 2024-12-21 | [50206](https://github.com/airbytehq/airbyte/pull/50206) | Update dependencies |
| 0.5.2 | 2024-12-14 | [49543](https://github.com/airbytehq/airbyte/pull/49543) | Update dependencies |
| 0.5.1 | 2024-12-12 | [49025](https://github.com/airbytehq/airbyte/pull/49025) | Update dependencies |
| 0.5.0 | 2024-10-28 | [47262](https://github.com/airbytehq/airbyte/pull/47262) | Migrate to Manifest-only |
| 0.4.14 | 2024-10-28 | [47072](https://github.com/airbytehq/airbyte/pull/47072) | Update dependencies |
| 0.4.13 | 2024-10-12 | [46842](https://github.com/airbytehq/airbyte/pull/46842) | Update dependencies |
| 0.4.12 | 2024-10-05 | [46500](https://github.com/airbytehq/airbyte/pull/46500) | Update dependencies |
| 0.4.11 | 2024-09-28 | [46157](https://github.com/airbytehq/airbyte/pull/46157) | Update dependencies |
| 0.4.10 | 2024-09-21 | [45766](https://github.com/airbytehq/airbyte/pull/45766) | Update dependencies |
| 0.4.9 | 2024-09-14 | [45542](https://github.com/airbytehq/airbyte/pull/45542) | Update dependencies |
| 0.4.8 | 2024-09-07 | [45210](https://github.com/airbytehq/airbyte/pull/45210) | Update dependencies |
| 0.4.7 | 2024-08-31 | [44978](https://github.com/airbytehq/airbyte/pull/44978) | Update dependencies |
| 0.4.6 | 2024-08-24 | [44652](https://github.com/airbytehq/airbyte/pull/44652) | Update dependencies |
| 0.4.5 | 2024-08-17 | [44272](https://github.com/airbytehq/airbyte/pull/44272) | Update dependencies |
| 0.4.4 | 2024-08-12 | [43851](https://github.com/airbytehq/airbyte/pull/43851) | Update dependencies |
| 0.4.3 | 2024-08-10 | [43467](https://github.com/airbytehq/airbyte/pull/43467) | Update dependencies |
| 0.4.2 | 2024-08-03 | [43154](https://github.com/airbytehq/airbyte/pull/43154) | Update dependencies |
| 0.4.1 | 2024-07-27 | [42779](https://github.com/airbytehq/airbyte/pull/42779) | Update dependencies |
| 0.4.0 | 2024-07-18 | [41443](https://github.com/airbytehq/airbyte/pull/41443) | Add TimeOff Requests stream |
| 0.3.8 | 2024-07-20 | [42200](https://github.com/airbytehq/airbyte/pull/42200) | Update dependencies |
| 0.3.7 | 2024-07-13 | [41780](https://github.com/airbytehq/airbyte/pull/41780) | Update dependencies |
| 0.3.6 | 2024-07-10 | [41437](https://github.com/airbytehq/airbyte/pull/41437) | Update dependencies |
| 0.3.5 | 2024-07-09 | [41088](https://github.com/airbytehq/airbyte/pull/41088) | Update dependencies |
| 0.3.4 | 2024-07-06 | [40818](https://github.com/airbytehq/airbyte/pull/40818) | Update dependencies |
| 0.3.3 | 2024-06-25 | [40288](https://github.com/airbytehq/airbyte/pull/40288) | Update dependencies |
| 0.3.2 | 2024-06-22 | [40156](https://github.com/airbytehq/airbyte/pull/40156) | Update dependencies |
| 0.3.1 | 2024-06-06 | [39201](https://github.com/airbytehq/airbyte/pull/39201) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.0 | 2024-05-25 | [37452](https://github.com/airbytehq/airbyte/pull/37452) | Migrate to Low Code |
| 0.2.6 | 2024-04-19 | [37124](https://github.com/airbytehq/airbyte/pull/37124) | Updating to 0.80.0 CDK |
| 0.2.5 | 2024-04-18 | [37124](https://github.com/airbytehq/airbyte/pull/37124) | Manage dependencies with Poetry. |
| 0.2.4 | 2024-04-15 | [37124](https://github.com/airbytehq/airbyte/pull/37124) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.3 | 2024-04-12 | [37124](https://github.com/airbytehq/airbyte/pull/37124) | schema descriptions |
| 0.2.2 | 2022-09-16 | [17684](https://github.com/airbytehq/airbyte/pull/17684) | Fix custom field validation retrieve |
| 0.2.1 | 2022-09-16 | [16826](https://github.com/airbytehq/airbyte/pull/16826) | Add custom fields validation during check |
| 0.2.0 | 2022-03-24 | [11326](https://github.com/airbytehq/airbyte/pull/11326) | Add support for Custom Reports endpoint |
| 0.1.0 | 2021-08-27 | [5054](https://github.com/airbytehq/airbyte/pull/5054) | Initial release with Employees API |

</details>

</HideInUI>
