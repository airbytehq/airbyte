# Zenefits

This page contains the setup guide and reference information for the Zenefits source connector.

## Prerequisites

- Access to the Zenefits account where you want to integrate Airbyte.
- A Zenefits API token. Follow the steps given below to obtain the token.

### Obtaining the Zenefits API Token

1. Sign in to your Zenefits account.
2. Navigate to the [Zenefits Developer Dashboard](https://developers.zenefits.com/dashboard).
3. In the Dashboard, click on **Create New Project**.
4. Enter all the relevant details for your project and click **Submit**.
5. Once the project is created, click the **Settings** tab.
6. Under the **API Permissions** section, select the data scopes that you want to grant access to Airbyte.
7. Click the **Save** button to save API Permissions.
8. Click the **Authentication** tab.
9. Copy the token displayed under **Bearer Token**. This token will be used while setting up the Zenefits source connector in Airbyte.

For more details, please refer to the [Zenefits API Authentication Documentation](https://developers.zenefits.com/v1.0/docs/auth).

## Set up Zenefits as a source in Airbyte

To set up Zenefits as a source in Airbyte, simply fill out the configuration form with the required information:

1. For **Token**, paste the Zenefits API token obtained from your Zenefits Developer Dashboard.
2. Click **Set up source**.

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