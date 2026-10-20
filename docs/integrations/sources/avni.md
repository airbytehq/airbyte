# Avni

This page contains the setup guide and reference information for the [Avni](https://avniproject.org/) source connector. The connector reads subjects, program enrolments, program encounters, and general encounters from the [Avni API](https://avni.readme.io/docs/api-guide).

## Prerequisites

- An Avni account on the Avni hosted service at `app.avniproject.org`. The connector sends all requests to `https://app.avniproject.org/api` and signs in through the Avni hosted service's Amazon Cognito user pool, so it doesn't work with self-hosted Avni servers.
- The username and password of an Avni user that the connector can sign in as.

## Setup guide

### Step 1: Prepare an Avni user

1. In the Avni Admin web app, create or choose the user that Airbyte signs in as. The [Avni API guide](https://avni.readme.io/docs/api-guide#authentication) recommends giving this user the **User** role.
2. Sign in to the Avni web app once as this user and set a permanent password. The connector uses the username and password directly, and it can't complete a password-change challenge on first sign-in.

### Step 2: Set up the Avni connector in Airbyte

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New Source**.
2. On the source setup page, select **Avni** from the Source type dropdown and enter a name for this connector.
3. Enter the **username** and **password** of your Avni user.
4. Enter the **start_date**. The connector syncs records that were last modified after this date and time. Use the format `yyyy-MM-ddTHH:mm:ss.SSSZ`, for example `2000-10-31T01:30:00.000Z`. The default is `2000-06-23T01:30:00.000Z`. To sync all data, use a date earlier than your oldest Avni record.
5. Click **Set up source**.

If Avni rejects the username or password, the connection check fails with an `Avni login failed` error that includes the message returned by Avni's authentication service.

## Supported sync modes

The Avni source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) (recommended)

## Supported streams

| Stream | Avni endpoint | Description |
| :----- | :------------ | :---------- |
| `subjects` | `/api/subjects` | Registered subjects. Subjects are the top-level entity in Avni. |
| `program_enrolments` | `/api/programEnrolments` | Enrolments of subjects in programs. |
| `program_encounters` | `/api/programEncounters` | Encounters that take place within a program enrolment. |
| `encounters` | `/api/encounters` | Encounters of subjects that aren't part of a program. |

All streams use `ID` as the primary key and support incremental syncs.

### Incremental sync behavior

Each stream uses `last_modified_at` as its cursor field. The connector adds this field to every record by copying the `Last modified at` value from the record's `audit` object.

On each sync, the connector requests records modified between the saved cursor value (or the **start_date** on the first sync) and 10 seconds before the sync started. Records modified in the last 10 seconds before a sync starts are picked up by the next sync. Avni returns updated records again each time they change, so use **Incremental Sync - Append + Deduped** to keep only the latest version of each record.

The connector requests 100 records per page.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.1.2 | 2026-10-20 | [88141](https://github.com/airbytehq/airbyte/pull/88141) | Migrate to manifest-only and replace the custom Cognito authenticator with declarative authentication; removes the boto3 dependency. |
| 0.1.1 | 2025-02-27 | [54696](https://github.com/airbytehq/airbyte/pull/54696) | Update requests-mock version |
| 0.1.0 | 2024-03-27 | [30222](https://github.com/airbytehq/airbyte/pull/30222) | Avni Source Connector |

</details>
