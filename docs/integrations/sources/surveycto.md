# SurveyCTO

This page guides you through the process of setting up the SurveyCTO source connector.

## Prerequisites

- Server Name `The name of the ServerCTO server`
- Your SurveyCTO `Username`
- Your SurveyCTO `Password`
- Form ID `Unique Identifier for one of your forms`
- Start Date `Start Date default`
- ### Optional Fields
  - Dataset Id - Dataset ids for survey cto. It is required when getting data from dataset instead of a form
  - Key - SurveyCTo enryption key. This is required if you're pulling data from an encrypted form/dataset
  - Media Files - This is where the urls for the form mediafiles are stored. It can be stored in S3 or locally. If stored in S3, the `bucket`, `access_key_id`, `secret_access_key`, `region_name`, `file_key` and `url_column` are required. If stored locally, the `path`, `file_name` and `url_column` are required.

## How to setup a SurveyCTO Account

- create the account
- create your form
- publish your form
- give your user an API consumer permission to the existing role or create a user with that role and permission.

## Set up the SurveyCTO source connection

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
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

The SurveyCTO source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- (Recommended)[ Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

The SurveyCTO source connector supports the following streams:

- Form Data
- Form Dataset - To pull .csv data for a server dataset from a SurveyCTO server.
- Mediafiles - Currently, the stream is set up to accept a CSV file containing three columns: `file_name`, `file_type`, and `url_column`. This CSV is retrieved from an S3 bucket by the stream. While additional destinations are slated for future integration, the immediate output of the stream is a binary string encoding of the media files, such as images or audio. To revert these files to their original formats, a separate connector has been developed with the specific task of decoding the binary strings and then storing the media back into an S3 bucket in their original format. This division in the process ensures that media files are both easily accessible and maintain their integrity throughout the handling process.
- Form Data Definition - Fetch form's definition from SurveyCTO in json format
- Form Repeat Groups - Fetch SurveyCTO form's repeat group data in csv format. The form needs to have repeat groups for it to work.

## Reference Resources
[SurveyCTO API Documentation](https://support.surveycto.com/hc/en-us/articles/360033156894?flash_digest=0a6eded7694409181788cc46a7026897850d65b5&flash_digest=d76dde7c3ffc40f4a7f0ebd87596d32f3a52304f) - Provides details of the SurveyCTO API endpoints and the expected parameters. The downside is you need to be signed in to a SurveyCTO server to access the documentation

[pysurveycto](https://github.com/IDinsight/surveycto-python) - A Python library to download data collected on SurveyCTO data collection app using SurveyCTO REST API. The library was created by [IDinsight](https://www.idinsight.org/) as an open-source contribution to the SurveyCTO ecosystem. 

## Changelog

| Version | Date | Pull Request | Subject |
| 0.1.3 | 2023-03-21 | [36346](https://github.com/airbytehq/airbyte/pull/36346) | Added New Streams |
| 0.1.2 | 2023-07-27 | [28512](https://github.com/airbytehq/airbyte/pull/28512) | Added Check Connection |
| 0.1.1 | 2023-04-25 | [24784](https://github.com/airbytehq/airbyte/pull/24784) | Fix incremental sync |
| 0.1.0 | 2022-11-16 | [19371](https://github.com/airbytehq/airbyte/pull/19371) | SurveyCTO Source Connector |
