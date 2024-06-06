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
| :------ | :--------- | :----------- | :-------------------------------------------------------- |
| 0.1.5 | 2024-06-06 | [39198](https://github.com/airbytehq/airbyte/pull/39198) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4   | 2024-05-16 | #38181       | Add explicit projection when reading from Astra DB        |
| 0.1.3   | 2024-04-19 | #37405       | Add "airbyte" user-agent in the HTTP requests to Astra DB |
| 0.1.2   | 2024-04-15 |              | Moved to Poetry; Updated CDK & pytest versions            |
| 0.1.1   | 2024-01-26 |              | DS Branding Update                                        |
| 0.1.0   | 2024-01-08 |              | Initial Release                                           |

</details>
