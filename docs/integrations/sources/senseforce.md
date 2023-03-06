# Senseforce

This page guides you through the process of setting up the Senseforce source connector.

## Sync overview

## Prerequisites
- A [Senseforce Dataset](https://manual.senseforce.io/manual/sf-platform/dataset-builder) to export
- Your [Senseforce `API Access Token`](https://manual.senseforce.io/manual/sf-platform/public-api/get-your-access-token)
- Your [Senseforce `Backend URL`](https://manual.senseforce.io/manual/sf-platform/public-api/endpoints#prerequisites)
- Your [Senseforce `Dataset ID`](https://manual.senseforce.io/manual/sf-platform/public-api/endpoints#prerequisites)

## Creating a Senseforce Dataset to Export
The Senseforce Airbyte connector allows to export custom datasets built bei Senseforce users. Follow these steps to configure a dataset which can be exported with the Airbyte connector: 
1. Create a new, empty dataset as documented [here](https://manual.senseforce.io/manual/sf-platform/dataset-builder)
2. Add at least the following columns (these columns are Senseforce system columns and available for all of your custom data models/event schemas): 
   1. Metadata -> Timestamp
   2. Metadata -> Thing
   3. Metadata -> Id
3. Add any other column of your event schemas you want to export
4. Enter a descriptive Name and a Description and save the dataset
5. Note the ID of the dataset (the GUID at the end of the URL path of your dataset in your browser URL bar)

> **Tip:** For most exports it is recommended to have the Timestamp column in first place. The Airbyte connector automatically orders in ascending direction. If the Timestamp column is not in the first position, incremental syncs might not work properly.

> **IMPORTANT:** The Timestamp, Thing and Id column are mandatory for the Connector to work as intended. While it still works without eg. the "Id", functionality might be impaired if one of these 3 columns is missing. Make sure to not rename these columns - keep them at their default names.


## Set up the Senseforce source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Senseforce** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Access Token**, enter your [Senseforce `API Access Token`](https://manual.senseforce.io/manual/sf-platform/public-api/get-your-access-token).
6. For **Senseforce backend URL**, enter your [Senseforce `Backend URL`](https://manual.senseforce.io/manual/sf-platform/public-api/endpoints#prerequisites).
6. For **Dataset ID**, enter your [Senseforce `Dataset ID`](https://manual.senseforce.io/manual/sf-platform/public-api/endpoints#prerequisites).

   We recommend creating an api access token specifically for Airbyte to control which resources Airbyte can access. For good operations, we recommend to create a separate Airbyte User as well as a separate Senseforce [Airbyte Group](https://manual.senseforce.io/manual/sf-platform/user-and-group-management). Share the dataset with this group and grant Dataset Read, Event Schema Read and Machine Master Data Read permissions.  

7. For **The first day (in UTC) when to read data from**, enter the day in YYYY-MM-DD format. The data added on and after this day will be replicated.
9. Click **Set up source**.

## Supported sync modes

The Senseforce source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

> **NOTE:** The Senseforce Airbyte connector uses the Timestamp column to determine, which data were already read. Data inserted AFTER a finished sync, with timestamps less than already synced ones, are not considered for the next sync anymore.
If this behavior does not fit your use case, follow the next section
### Using Inserted Timestamp instead of Data Timestamp for incremental modes
1. Rename your "Timestamp" column to "Timestamp_data"
2. Add the Metadata -> Inserted column to your dataset.
3. Move the newly added "Inserted" column to position 1.
4. Rename the "Inserted" column to "Timestamp".

Now the inserted timestamp will be used for creating the Airbyte cursor. Note that this method results in slower syncs, as the Senseforce queries to generate the Datasets are slower than if you use the data timestamp.

## Supported Streams

The Senseforce source connector supports the following streams:
- [Senseforce Datasets](https://manual.senseforce.io/manual/sf-platform/public-api/endpoints)


### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |

### Performance considerations

Senseforce utilizes an undocumented rate limit which - under normal use - should not be triggered, even with huge datasets.
[Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.1   | 2023-02-13 | [22892](https://github.com/airbytehq/airbyte/pull/22892) | Specified date formatting in specification |
| 0.1.0   | 2022-10-26 | [#18775](https://github.com/airbytehq/airbyte/pull/18775) | 🎉 New Source: Mailjet SMS API [low-code CDK] |
