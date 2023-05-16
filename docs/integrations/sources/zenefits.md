# Zenefits

This page contains the setup guide and reference information for the Zenefits source connector.


## Prerequisites

- A Zenefits [token](https://developers.zenefits.com/v1.0/docs/auth)


## Set up Zenefits as a source in Airbyte

1. In the **Zenefits Integration Spec** section of the **Create New Connection** screen, enter your Zenefits token. 
    - To obtain your token, please navigate to the [Zenfitis Authentication page](https://developers.zenefits.com/v1.0/docs/auth). 
    - Click on the **"Use Sync with Zenefits"** button on the page. 
    - Follow the steps and copy the token generated.
2. For the **Name** field, enter a name for the Zenefits connector.
3. Click **Create**.


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


Note: Please do not update anything in the Changelog or Features section as it may break the system.