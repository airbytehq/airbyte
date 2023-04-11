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

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| `0.1.0` | 2022-08-24 | [14809](https://github.com/airbytehq/airbyte/pull/14809) | Initial Release |
