# Aircall

This page contains the setup guide and reference information for the [Aircall](https://developer.aircall.io/api-references/#rest-api) source

## Prerequisites

Access Token (which acts as bearer token) is mandate for this connector to work, It could be seen at settings (ref - https://dashboard.aircall.io/integrations/api-keys).

## Setup guide

### Step 1: Set up Aircall connection

- Get an Aircall access token via settings (ref - https://dashboard.aircall.io/integrations/api-keys)
- Setup params (All params are required)
- Available params
  - api_id: The auto generated id
  - api_token: Seen at the Aircall settings (ref - https://dashboard.aircall.io/integrations/api-keys)
  - start_date: Date filter for eligible streams, enter

### Step 2: Set up the Aircall connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Aircall connector and select **Aircall** from the Source type dropdown.
4. Enter your `api_id, api_token and start_date`.
5. Click **Set up source**.

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_id, api_token and start_date`.
4. Click **Set up source**.

## Supported sync modes

The Aircall source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- calls
- company
- contacts
- numbers
- tags
- user_availability
- users
- teams
- webhooks

## API method example

GET https://api.aircall.io/v1/numbers

## Performance considerations

Aircall [API reference](https://api.aircall.io/v1) has v1 at present. The connector as default uses v1.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                   | Subject                     |
| :------ | :--------- | :----------------------------------------------------------------------------- | :-------------------------- |
| 0.2.1   | 2024-06-06 | [38454](https://github.com/airbytehq/airbyte/pull/38454)          | [autopull] base image + poetry + up_to_date |
| 0.2.0   | 2023-06-20 | [Correcting availablity typo](https://github.com/airbytehq/airbyte/pull/27433) | Correcting availablity typo |
| 0.1.0   | 2023-04-19 | [Init](https://github.com/airbytehq/airbyte/pull/)                             | Initial commit              |

</details>
