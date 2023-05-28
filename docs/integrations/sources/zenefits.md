# Zenefits

This page contains the setup guide and reference information for the Zenefits source connector.

## Prerequisites

- A Zenefits [token](https://developers.zenefits.com/v1.0/docs/auth)

## Setup Guide

This guide will help you set up the Zenefits Source connector in Airbyte. Before you begin, ensure that you have an active Zenefits account. If you do not have one, please [sign up for an account](https://www.zenefits.com/) or contact your Zenefits administrator.

### Obtain Zenefits API Token

1. Visit the [Zenefits Developers home page](https://developers.zenefits.com/) and sign in with your Zenefits credentials.

2. Click on **My Apps** in the top navigation bar.

3. Click on **Create New App**.

4. Fill in the required fields: App Name, Redirect URIs, and App permissions. For Redirect URIs, input any placeholder URI; this will not be used in Airbyte's connection.

5. Once your app is created, visit the **App Details** page.

6. Click on the **Sync with Zenefits** button. A new window will open requesting authorization for your app.

7. After authorizing the app, you will be redirected to the URI specified earlier. The Zenefits API token will be included in the URL as a query parameter named `access_token`. Extract this token for use in the Airbyte configuration.

### Configure Zenefits Source

1. Enter a name for your Zenefits connector in the **Name** field.

2. Input the extracted API token into the **Token** field.

3. Click on **Set up source** to complete the configuration process.

That's it! Zenefits is now set up as a Source connector in Airbyte.

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
