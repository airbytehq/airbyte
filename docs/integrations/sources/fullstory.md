# FullStory

This page contains the setup guide and reference information for the [FullStory](https://developer.fullstory.com/) source

## Prerequisites

API Key (which acts as bearer token) is mandate for this connector to work, It could be seen at settings (ref - https://app.fullstory.com/ui/o-1K942V-na1/settings/apikeys).

## Setup guide

### Step 1: Set up FullStory connection

- Get a FullStory api key via settings (ref - https://app.fullstory.com/ui/o-1K942V-na1/settings/apikeys)
- Setup params (All params are required)
- Available params
  - api_key: The generated api key
  - uid: The unique identifier which can be configured in the fullstory script, under FS.identify
  - start_date: Date filter for eligible streams, enter

## Step 2: Set up the FullStory connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the FullStory connector and select **FullStory** from the Source type dropdown.
4. Enter your `api_key, uid and start_date`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_id, api_token and start_date`.
4. Click **Set up source**.

## Supported sync modes

The FullStory source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

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
- user_availablity
- users
- teams
- webhooks

## API method example

GET https://api.fullstory.com/segments/v1

## Performance considerations

FullStory [API reference](https://api.fullstory.com) has v1 at present. The connector as default uses v1.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                       | Subject        |
| :------ | :--------- | :------------------------------------------------- | :------------- |
| 0.1.1 | 2024-05-20 | [38420](https://github.com/airbytehq/airbyte/pull/38420) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2023-04-25 | [Init](https://github.com/airbytehq/airbyte/pull/) | Initial commit |

</details>