# SurveyCTO

This page guides you through the process of setting up the SurveyCTO source connector.

## Prerequisites

- Server Name `The name of the ServerCTO server`
- Your SurveCTO `Username`
- Your SurveyCTO `Password`
- Form ID `Unique Identifier for one of your forms`

## Set up the SurveyCTO source connection
1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Survey CTO** from the Source type dropdown.
4. Enter a name for your source.
5. Enter a Server name for your SurveyCTO account. 
6. Enter a Username for SurveyCTO account.
7. Enter a Password for SurveyCTO account.
8. Form ID's (We can multiple forms id here to pull from) 
9. Click **Set up source**.

## Supported sync modes

The Commcare source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Overwrite
- Incremental

## Supported Streams

The Commcare source connector supports the following streams:

- Forms

## Changelog

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
