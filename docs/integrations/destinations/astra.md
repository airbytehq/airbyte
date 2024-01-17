# Astra Destination

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
-- Because database names can’t be changed later, it’s best to name your database something meaningful. Database names must start and end with an alphanumeric character, and may contain the following special characters: & + - _ ( ) < > . , @.
- Select your preferred Provider and Region.
-- You can select from a limited number of regions if you’re on the Free plan. Regions with a lock icon require that you upgrade to a Pay As You Go plan.
- Click Create Database.
-- You are redirected to your new database’s Overview screen. Your database starts in Pending status before transitioning to Initializing. You’ll receive a notification once your database is initialized.

#### Setting up a Vector Collection

- From the database Overview screen, click on the Data Explorer tab
- Either enter default_namespace into the Airbyte UI under astra_db_keyspace or open the namespace dropdown, create a new namespace, and enter that instead
- Click Create Collection
- Enter a name for the collection
-- Also enter this name into the Airbyte UI as collection
- Enter a vector length under Dimensions
-- This should match with the embedding model you plan to use. The default model for openai is text-embedding-ada-002 which produced vectors of length 1536.
- Select a similarity metric
-- Default is cosine

#### Gathering other credentials

- Go back to the Overview tab on the Astra UI
- Copy the Endpoint under Database Details and load into Airbyte under the name astra_db_endpoint
- Click generate token, copy the application token and load under astra_db_app_token

## Supported Sync Modes

Full Refresh Sync

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2024-01-08 |                                                          | Initial Release             |
