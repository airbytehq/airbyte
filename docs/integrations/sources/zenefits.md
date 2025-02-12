# Zenefits

This page contains the setup guide and reference information for the Zenefits source connector.

## Prerequisites

- A Zenefits [token](https://developers.zenefits.com/v1.0/docs/auth)

## Set up Zenefits as a source in Airbyte

### For Airbyte OSS

To set up Zenefits as a source in Airbyte Cloud:

1.  In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
2.  On the Set up the source page, select **Zenefits** from the **Source type** dropdown.
3.  For Name, enter a name for the Zenefits connector.
4.  For **Token**, enter the token you have got from [Authentication](https://developers.zenefits.com/v1.0/docs/auth)
5.  Click **Set up source**.

## Supported sync modes

The Zenefits source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)

## Supported Streams

You can replicate the following tables using the Zenefits connector:

- [People](https://developers.zenefits.com/docs/people)
- [Employments](https://developers.zenefits.com/docs/employment)
- [Vacation_requests](https://developers.zenefits.com/docs/vacation-requests)
- [Vacation_types](https://developers.zenefits.com/docs/vacation-types)
- [Time_durations](https://developers.zenefits.com/docs/time-durations)
- [Departments](https://developers.zenefits.com/docs/department)
- [Locations](https://developers.zenefits.com/docs/location)
- [Labor_groups](https://developers.zenefits.com/docs/labor-groups)
- [Labor_group_types](https://developers.zenefits.com/docs/labor-group-types)
- [Custom_fields](https://developers.zenefits.com/docs/custom-fields)
- [Custom_field_values](https://developers.zenefits.com/docs/custom-field-values)

## Data type mapping

| Integration Type | Airbyte Type |
| :--------------: | :----------: |
|      string      |    string    |
|      number      |    number    |
|      array       |    array     |
|      object      |    object    |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.9 | 2025-02-08 | [53594](https://github.com/airbytehq/airbyte/pull/53594) | Update dependencies |
| 0.3.8 | 2025-02-01 | [53116](https://github.com/airbytehq/airbyte/pull/53116) | Update dependencies |
| 0.3.7 | 2025-01-25 | [52546](https://github.com/airbytehq/airbyte/pull/52546) | Update dependencies |
| 0.3.6 | 2025-01-18 | [51941](https://github.com/airbytehq/airbyte/pull/51941) | Update dependencies |
| 0.3.5 | 2025-01-11 | [51410](https://github.com/airbytehq/airbyte/pull/51410) | Update dependencies |
| 0.3.4 | 2024-12-28 | [50838](https://github.com/airbytehq/airbyte/pull/50838) | Update dependencies |
| 0.3.3 | 2024-12-21 | [50365](https://github.com/airbytehq/airbyte/pull/50365) | Update dependencies |
| 0.3.2 | 2024-12-14 | [47648](https://github.com/airbytehq/airbyte/pull/47648) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-01 | [42950](https://github.com/airbytehq/airbyte/pull/42950) | Refactor connector to manifest-only format |
| 0.2.13 | 2024-07-27 | [42668](https://github.com/airbytehq/airbyte/pull/42668) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42153](https://github.com/airbytehq/airbyte/pull/42153) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41810](https://github.com/airbytehq/airbyte/pull/41810) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41535](https://github.com/airbytehq/airbyte/pull/41535) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41298](https://github.com/airbytehq/airbyte/pull/41298) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40765](https://github.com/airbytehq/airbyte/pull/40765) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40264](https://github.com/airbytehq/airbyte/pull/40264) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40055](https://github.com/airbytehq/airbyte/pull/40055) | Update dependencies |
| 0.2.5 | 2024-06-04 | [39086](https://github.com/airbytehq/airbyte/pull/39086) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.4 | 2024-04-19 | [37303](https://github.com/airbytehq/airbyte/pull/37303) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37303](https://github.com/airbytehq/airbyte/pull/37303) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37303](https://github.com/airbytehq/airbyte/pull/37303) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37303](https://github.com/airbytehq/airbyte/pull/37303) | schema descriptions |
| 0.2.0 | 2023-10-29 | [31946](https://github.com/airbytehq/airbyte/pull/31946) | Migrate to Low Code |
| 0.1.0 | 2022-08-24 | [14809](https://github.com/airbytehq/airbyte/pull/14809) | Initial Release |
