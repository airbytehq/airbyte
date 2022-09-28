# Commcare

This page guides you through the process of setting up the Commcare source connector.

## Prerequisites

- Your Commcare API Key

## Set up the Commcare source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Commcare** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key**, enter your Commcare API Key.
6. Click **Set up source**.

## Supported sync modes

The Commcare source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Overwrite

## Supported Streams

The Commcare source connector supports the following streams:

- Case
- Form

## Changelog

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
