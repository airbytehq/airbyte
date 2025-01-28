# Astra DB Destination

This page contains the setup guide and reference information for the destination-astra connector.

## Pre-Requisites

- An OpenAI, AzureOpenAI, Cohere, etc. API Key

## Setup Guide

#### Set Up an Astra Database

- Create an Astra account [here](https://astra.datastax.com/signup)
- In the Astra Portal, select Databases in the main navigation.
- Click Create Database.
- In the Create Database dialog, select the Serverless (Vector) deployment type.
- In the Configuration section, enter a name for the new database in the Database name field.
  -- Because database names can’t be changed later, it’s best to name your database something meaningful. Database names must start and end with an alphanumeric character, and may contain the following special characters: & + - \_ ( ) < > . , @.
- Select your preferred Provider and Region.
  -- You can select from a limited number of regions if you’re on the Free plan. Regions with a lock icon require that you upgrade to a Pay As You Go plan.
- Click Create Database.
  -- You are redirected to your new database’s Overview screen. Your database starts in Pending status before transitioning to Initializing. You’ll receive a notification once your database is initialized.

#### Gathering other credentials

- Go back to the Overview tab on the Astra UI
- Copy the Endpoint under Database Details and load into Airbyte under the name astra_db_endpoint
- Click generate token, copy the application token and load under astra_db_app_token

## Supported Sync Modes

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                   |
|:--------| :--------- | :----------- |:----------------------------------------------------------|
| 0.1.36 | 2025-01-25 | [52179](https://github.com/airbytehq/airbyte/pull/52179) | Update dependencies |
| 0.1.35 | 2025-01-11 | [51295](https://github.com/airbytehq/airbyte/pull/51295) | Update dependencies |
| 0.1.34 | 2025-01-04 | [50910](https://github.com/airbytehq/airbyte/pull/50910) | Update dependencies |
| 0.1.33 | 2024-12-28 | [50446](https://github.com/airbytehq/airbyte/pull/50446) | Update dependencies |
| 0.1.32 | 2024-12-21 | [50213](https://github.com/airbytehq/airbyte/pull/50213) | Update dependencies |
| 0.1.31 | 2024-12-14 | [49288](https://github.com/airbytehq/airbyte/pull/49288) | Update dependencies |
| 0.1.30 | 2024-11-25 | [48674](https://github.com/airbytehq/airbyte/pull/48674) | Update dependencies |
| 0.1.29 | 2024-10-29 | [47105](https://github.com/airbytehq/airbyte/pull/47105) | Update dependencies |
| 0.1.28 | 2024-10-12 | [46857](https://github.com/airbytehq/airbyte/pull/46857) | Update dependencies |
| 0.1.27 | 2024-10-05 | [46402](https://github.com/airbytehq/airbyte/pull/46402) | Update dependencies |
| 0.1.26 | 2024-09-28 | [46179](https://github.com/airbytehq/airbyte/pull/46179) | Update dependencies |
| 0.1.25 | 2024-09-21 | [45829](https://github.com/airbytehq/airbyte/pull/45829) | Update dependencies |
| 0.1.24 | 2024-09-14 | [45498](https://github.com/airbytehq/airbyte/pull/45498) | Update dependencies |
| 0.1.23 | 2024-09-07 | [45330](https://github.com/airbytehq/airbyte/pull/45330) | Update dependencies |
| 0.1.22 | 2024-08-31 | [44983](https://github.com/airbytehq/airbyte/pull/44983) | Update dependencies |
| 0.1.21 | 2024-08-24 | [44700](https://github.com/airbytehq/airbyte/pull/44700) | Update dependencies |
| 0.1.20 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.19 | 2024-08-17 | [44319](https://github.com/airbytehq/airbyte/pull/44319) | Update dependencies |
| 0.1.18 | 2024-08-12 | [43811](https://github.com/airbytehq/airbyte/pull/43811) | Update dependencies |
| 0.1.17 | 2024-08-10 | [43598](https://github.com/airbytehq/airbyte/pull/43598) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43075](https://github.com/airbytehq/airbyte/pull/43075) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42805](https://github.com/airbytehq/airbyte/pull/42805) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42251](https://github.com/airbytehq/airbyte/pull/42251) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41698](https://github.com/airbytehq/airbyte/pull/41698) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41451](https://github.com/airbytehq/airbyte/pull/41451) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41095](https://github.com/airbytehq/airbyte/pull/41095) | Update dependencies |
| 0.1.10 | 2024-07-06 | [40779](https://github.com/airbytehq/airbyte/pull/40779) | Update dependencies |
| 0.1.9 | 2024-06-29 | [40626](https://github.com/airbytehq/airbyte/pull/40626) | Update dependencies |
| 0.1.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.7 | 2024-06-25 | [40467](https://github.com/airbytehq/airbyte/pull/40467) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40162](https://github.com/airbytehq/airbyte/pull/40162) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39198](https://github.com/airbytehq/airbyte/pull/39198) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4   | 2024-05-16 | #38181       | Add explicit projection when reading from Astra DB        |
| 0.1.3   | 2024-04-19 | #37405       | Add "airbyte" user-agent in the HTTP requests to Astra DB |
| 0.1.2   | 2024-04-15 |              | Moved to Poetry; Updated CDK & pytest versions            |
| 0.1.1   | 2024-01-26 |              | DS Branding Update                                        |
| 0.1.0   | 2024-01-08 |              | Initial Release                                           |

</details>
