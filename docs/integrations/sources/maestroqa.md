# Maestro QA

[Maestro QA](https://www.maestroqa.com/) is a call center quality assurance software.

## Set up the Maestro QA connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Maestro QA** from the Source type dropdown.
4. Enter a name for your source.
5. For **API token**, enter the API token for your Maestro QA account.
6. For **Start date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The Maestro QS source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

 - Full Refresh
 - Incremental

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| 0.0.1   | 2023-03-17 |    | Release Maestro QA CDK Connector                     |
