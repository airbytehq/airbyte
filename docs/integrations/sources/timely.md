# Timely

This page contains the setup guide and reference information for the Asana source connector.

## Prerequisites

Please follow these [steps](https://dev.timelyapp.com/#authorization) to obtain Bearer Token for your account.

## Setup guide
## Step 1: Set up the Asana connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Asana connector and select **Asana** from the Source type dropdown.
4. Select `Authenticate your account`.
5. Log in and Authorize to the Asana account and click `Set up source`.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `personal_access_token`
4. Click **Set up source**

## Supported sync modes

The Asana source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |




---
description: 'This connector extracts "events" from Timely'
---

# Timely

Timely can track time spent in every web and desktop app automatically for you. Get a precise daily record of all the time you spend in documents, meetings, emails, websites and video calls with zero effort.[Timely APIs](https://dev.timelyapp.com/).

Timely uses [Events](https://dev.timelyapp.com/#events) to store all the entries a user makes. Users can add, delete and edit all entries. Some user’s actions are restricted based on their access level in Timely.

# Timely credentials

You should be able to create a Timely `Bearer Token` as described in [Intro to the Timely API](https://dev.timelyapp.com/#authorization)

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Initial release |
