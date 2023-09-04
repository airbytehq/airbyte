# Moengage

This page contains the setup guide and reference information for the Moengage source connector.

## Prerequisites

**For Airbyte Open Source:**

- Data center (Found After login)
- Data API ID (Found After login)
- Data API Key (Found After login)
- App ID (Found After login)
- Api secret (Found After login)

## Setup guide

### Step 1: Set up Moengage account and forms

1. Signup on [Moengage](https://dashboard-01.moengage.com/v4/#/auth) to create an account.
2. Login with that created account and move to dashboard

### Step 2: Set up the Moengage connector in Airbyte

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New Source**.
3. On the source setup page, select **Moengage** from the Source type dropdown and enter a name for this connector.
4. Enter the **Data center**, **Data API ID**, **Data API Key**, **APP ID**, and **API secret** of your Moengage account
5. Enter the Start Date
6. Click **Set up source**.

## Supported sync modes

The Moengage source connector supports the following[sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
​
- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported Streams

The Moengage connector supports **forms** as the streams.

## Connector-specific features

​The Moengage box uses the [api v4](https://api-{data_center}.moengage.com/)

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2023-09-16 | [](https://github.com/airbytehq/airbyte/pull/) | Initial Release |