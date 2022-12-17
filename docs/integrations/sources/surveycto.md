# SurveyCTO

This page guides you through the process of setting up the SurveyCTO source connector.

## Prerequisites

- Server Name `The name of the ServerCTO server`
- Your SurveCTO `Username`
- Your SurveyCTO `Password`
- Form ID `Unique Identifier for one of your forms`
- Start Date `Start Date default`

## How to setup a SurveyCTO Account
- create the account
- create your form
- publish your form
- give your user an API consumer permission to the existing role or create a user with that role and permission.

## Set up the SurveyCTO source connection
1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Survey CTO** from the Source type dropdown.
4. Enter a name for your source.
5. Enter a Server name for your SurveyCTO account. 
6. Enter a Username for SurveyCTO account.
7. Enter a Password for SurveyCTO account.
8. Form ID's (We can multiple forms id here to pull from) 
9. Start Date (This can be pass to pull the data from particular date)
10. Click **Set up source**.

## Supported sync modes

The Commcare source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* (Recommended)[ Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The Commcare source connector supports the following streams:

- Forms

## Changelog

| Version | Date | Pull Request | Subject |
| 0.1.0   | 2022-11-16 | [19371](https://github.com/airbytehq/airbyte/pull/19371)   | SurveyCTO Source Connector |
