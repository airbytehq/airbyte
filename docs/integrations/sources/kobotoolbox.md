# Kobotoolbox

This page contains the setup guide and reference information for the Kobotoolbox source connector.

## Prerequisites

**For Airbyte Open Source:**

- Username of Kobotoolbox account
- Password of Kobotoolbox account

## Setup guide

### Step 1: Set up Kobotoolbox account and forms

1. Signup on [Kobotoolbox](https://www.kobotoolbox.org/sign-up/) to create an account.
2. Create and deploy your custom form by following instructions given [here](https://support.kobotoolbox.org/new_form.html)

### Step 2: Set up the Kobotoolbox connector in Airbyte

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New Source**.
3. On the source setup page, select **Kobotoolbox** from the Source type dropdown and enter a name for this connector.
4. Enter the **username** and **password** of your kobotoolbox account
5. Enter the Start Date
6. Click **Set up source**.

## Supported sync modes

​
The Kobotoolbox source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
​

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- (Recommended)[ Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The Kobotoolbox connector supports **forms** as the streams.

## Note

- Normalization mode of data is not supported.
- For incremental sync please make sure your that you have selected MetaData "start time" and "end time" in kobo form settings.

## Connector-specific features

​The Kobotoolbox box uses the [api v2](https://kf.kobotoolbox.org/api/v2)

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2025-01-30 | [](https://github.com/airbytehq/airbyte/pull/) | Initial Release |