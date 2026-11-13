# Qualtrics

This page contains the setup guide and reference information for the [Qualtrics](https://api.qualtrics.com/) source connector.

## Prerequisites

- A Qualtrics account with API access enabled
- Your **Datacenter ID** (found in your Qualtrics account URL, e.g., `iad1` from `https://iad1.qualtrics.com`)
- One of the following authentication methods:
  - **API Token**: Found under Account Settings > Qualtrics IDs
  - **OAuth 2.0**: Client ID, Client Secret, and Refresh Token from a registered OAuth application
- (Optional) **Directory ID** — required only for syncing the Contacts stream
- (Optional) **Start Date** — for incremental sync of survey responses

## Setup guide

### Step 1: Obtain your Qualtrics credentials

1. Log into your Qualtrics account.
2. Navigate to **Account Settings > Qualtrics IDs** to find your Datacenter ID and API Token.
3. If using OAuth 2.0, register an OAuth application in your Qualtrics account to obtain Client ID, Client Secret, and Refresh Token.

### Step 2: Set up the Qualtrics connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter a name for the Qualtrics connector and select **Qualtrics** from the Source type dropdown.
4. Enter your **Datacenter ID**.
5. Choose your authentication method (API Token or OAuth 2.0) and enter the required credentials.
6. (Optional) Enter a **Start Date** for incremental sync of survey responses.
7. (Optional) Enter your **Directory ID** if you want to sync contacts.
8. Click **Set up source**.

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your **Datacenter ID** and authentication credentials.
4. (Optional) Configure Start Date and Directory ID.
5. Click **Set up source**.

## Supported sync modes

The Qualtrics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Stream | Sync Mode | Primary Key | Parent Stream |
| :----- | :-------- | :---------- | :------------ |
| surveys | Full Refresh | id | — |
| survey_questions | Full Refresh | QuestionID | surveys |
| survey_responses | Incremental | responseId | surveys |
| distributions | Full Refresh | id | surveys |
| contacts | Full Refresh | id | — |
| users | Full Refresh | id | — |
| groups | Full Refresh | id | — |

**Note:** The `contacts` stream requires a `directory_id` to be configured. The `survey_responses` stream supports incremental sync using the `lastModified` field.

## API method example

`GET https://{datacenter}.qualtrics.com/API/v3/surveys`

## Performance considerations

The Qualtrics API enforces rate limits. The connector includes automatic retry logic with a 30-second backoff for rate-limited requests (HTTP 429). For accounts with large numbers of surveys, initial syncs may take some time as survey-scoped streams (questions, responses, distributions) iterate over all surveys.

## Limitations & Troubleshooting

- The `contacts` stream will not sync unless a `directory_id` is provided in the connector configuration.
- OAuth 2.0 tokens are automatically refreshed when they expire.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.1.0   | 2026-03-03 | TBD          | Initial release |

</details>
