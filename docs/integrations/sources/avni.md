# Avni

This page contains the setup guide and reference information for the Avni source connector.

## Prerequisites

- Username of Avni account
- Password of Avni account

## Setup guide

### Step 1: Set up an Avni account

1. Signup on [Avni](https://avniproject.org/) to create an account.
2. Create Forms for Subjects Registrations, Programs Enrolment, Program Encounter using Avni Web Console -> [Getting Started](https://avniproject.org/getting-started/)
3. Register Subjects, Enrol them in Program using Avni Android Application [Here](https://play.google.com/store/apps/details?id=com.openchsclient&hl=en&gl=US)

### Step 2: Set up the Avni connector in Airbyte

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New Source**.
3. On the source setup page, select **Avni** from the Source type dropdown and enter a name for this connector.
4. Enter the **username** and **password** of your Avni account
5. Enter the **lastModifiedDateTime**, ALl the data which have been updated since this time will be returned. The Value should be specified in "yyyy-MM-dd'T'HH:mm:ss.SSSz", e.g. "2000-10-31T01:30:00.000Z". If all the data needed to be fetch keep this parameter to any old date or use e.g. date.
6. Click **Set up source**.

## Supported sync modes

The Avni source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
​

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- (Recommended)[ Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

Avni Source connector Support Following Streams:

- **Subjects Stream** : This stream provides details of registered subjects. You can retrieve information about subjects who have been registered in the system.
- **Program Enrolment Stream** : This stream provides program enrolment data. You can obtain information about subjects who have enrolled in programs.
- **Program Encounter Stream**, This stream provides data about encounters that occur within programs. You can retrieve information about all the encounters that have taken place within programs.
- **Subject Encounter Stream**, This stream provides data about encounters involving subjects, excluding program encounters. You can obtain information about all the encounters that subjects have had outside of program-encounter.

avirajsingh7 marked this conversation as resolved.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| 0.1.0 | 2023-09-07 | [30222](https://github.com/airbytehq/airbyte/pull/30222) | Avni Source Connector |

</details>