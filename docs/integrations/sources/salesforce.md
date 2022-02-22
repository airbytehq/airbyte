# Salesforce

## Overview

The Salesforce source supports both `Full Refresh` and `Incremental` syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

The Connector supports `Custom Fields` for each of their available streams

### Output schema

Several output streams are available from this source. A list of these streams can be found below in the [Streams](salesforce.md#streams) section.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

#### Incremental Deletes Sync
We can retrieve deleted records in Salesforce. It is available only for streams with the `IsDeleted` field in the schema. 
If the record was deleted, Salesforce set `IsDeleted=True` and in the next incremental sync, we read this record.
In case, when the record was created, synced, then updated and deleted, synced one more time, we retrieve the record with updated data and `IsDeleted=True`.

### Performance considerations

The connector is restricted by daily Salesforce rate limiting.
The connector uses as much rate limit as it can every day, then ends the sync early with success status and continues the sync from where it left the next time.
Note that, picking up from where it ends will work only for incremental sync.

## Getting started

### Requirements

* Salesforce Account
* Salesforce OAuth credentials
* Dedicated Salesforce user (optional)

**Note**: We recommend creating a new Salesforce user, restricted, read-only OAuth credentials specifically for Airbyte access. In addition, you can restrict access to only the data and streams you need by creating a profile in Salesforce and assigning it to the user.

### Setup guide

We recommend the following [walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) **while keeping in mind the edits we suggest below** for setting up a Salesforce app that can pull data from Salesforce and locating the credentials you need to provide to Airbyte.

Suggested edits:

1. If your salesforce URL does not take the form `X.salesforce.com`, use your actual Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`. 
2. When running a `curl` command, always run it with the `-L` option to follow any redirects.

#### is\_sandbox

If you log in using at [https://login.salesforce.com](https://login.salesforce.com), then the value is false. If you log in at [https://test.salesforce.com](https://test.salesforce.com) then the value should be true. If this is Greek to you, then this value should probably be false.

## Streams

**Note**: The connector supports reading not only standard streams, but also reading `Custom Objects`.

We fetch and handle all the possible & available streams dynamically based on:
- User Role & Permissions to read & fetch objects and their data (administration question);
- Whether or not, the stream has the queryable property is set to true, which means it's available to fetch the data, otherwise we will hit the 400 - bad request, or 503 - forbidden in response;
- No other restrictions applied, so we should have the full list of available streams as much as possible (both standard objects & custom ones along with standard and custom fields).

**Note**: Using the BULK API is not possible to receive data from the following streams:

* AcceptedEventRelation
* AssetTokenEvent
* AttachedContentNote
* Attachment
* CaseStatus
* ContractStatus
* DeclinedEventRelation
* EventWhoRelation
* FieldSecurityClassification
* OrderStatus
* PartnerRole
* QuoteTemplateRichTextData
* RecentlyViewed
* ServiceAppointmentStatus
* SolutionStatus
* TaskPriority
* TaskStatus
* TaskWhoRelation
* UndecidedEventRelation

## Changelog

| Version | Date       | Pull Request | Subject                                                                                                                          |
|:--------|:-----------| :--- |:---------------------------------------------------------------------------------------------------------------------------------|
| ???     | 2022-02-18 | [10454](https://github.com/airbytehq/airbyte/pull/10454) | Support incremental sync deletes                                                                                                 |
| 0.1.23  | 2022-02-10 | [10141](https://github.com/airbytehq/airbyte/pull/10141) | Processing of failed jobs                                                                                                        |
| 0.1.22  | 2022-02-02 | [10012](https://github.com/airbytehq/airbyte/pull/10012) | Increase CSV field_size_limit                                                                                                    |
| 0.1.21  | 2022-01-28 | [9499](https://github.com/airbytehq/airbyte/pull/9499) | If a sync reaches daily rate limit it ends the sync early with success status. Read more in `Performance considerations` section |
| 0.1.20  | 2022-01-26 | [9757](https://github.com/airbytehq/airbyte/pull/9757) | Parse CSV with "unix" dialect                                                                                                    |
| 0.1.19  | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description                                                                                        |
| 0.1.18  | 2022-01-20 | [9478](https://github.com/airbytehq/airbyte/pull/9478) | Add available stream filtering by `queryable` flag                                                                               |
| 0.1.17  | 2022-01-19 | [9302](https://github.com/airbytehq/airbyte/pull/9302) | Deprecate API Type parameter                                                                                                     |
| 0.1.16  | 2022-01-18 | [9151](https://github.com/airbytehq/airbyte/pull/9151) | Fix pagination in REST API streams                                                                                               |
| 0.1.15  | 2022-01-11 | [9409](https://github.com/airbytehq/airbyte/pull/9409) | Correcting the presence of an extra `else` handler in the error handling                                                         |
| 0.1.14  | 2022-01-11 | [9386](https://github.com/airbytehq/airbyte/pull/9386) | Handling 400 error, while `sobject` doesn't support `query` or `queryAll` requests                                               |
| 0.1.13  | 2022-01-11 | [8797](https://github.com/airbytehq/airbyte/pull/8797) | Switched from authSpecification to advanced_auth in specefication                                                                |
| 0.1.12  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871) | Fix `examples` for new field in specification                                                                                    |
| 0.1.11  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871) | Add the ability to filter streams by user                                                                                        |
| 0.1.10  | 2021-12-23 | [9005](https://github.com/airbytehq/airbyte/pull/9005) | Handling 400 error when a stream is not queryable                                                                                |
| 0.1.9   | 2021-12-07 | [8405](https://github.com/airbytehq/airbyte/pull/8405) | Filter 'null' byte(s) in HTTP responses                                                                                          |
| 0.1.8   | 2021-11-30 | [8191](https://github.com/airbytehq/airbyte/pull/8191) | Make `start_date` optional and change its format to `YYYY-MM-DD`                                                                 |
| 0.1.7   | 2021-11-24 | [8206](https://github.com/airbytehq/airbyte/pull/8206) | Handling 400 error when trying to create a job for sync using Bulk API.                                                          |
| 0.1.6   | 2021-11-16 | [8009](https://github.com/airbytehq/airbyte/pull/8009) | Fix retring of BULK jobs                                                                                                         |
| 0.1.5   | 2021-11-15 | [7885](https://github.com/airbytehq/airbyte/pull/7885) | Add `Transform` for output records                                                                                               |
| 0.1.4   | 2021-11-09 | [7778](https://github.com/airbytehq/airbyte/pull/7778) | Fix types for `anyType` fields                                                                                                   |
| 0.1.3   | 2021-11-06 | [7592](https://github.com/airbytehq/airbyte/pull/7592) | Fix getting `anyType` fields using BULK API                                                                                      |
| 0.1.2   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438) | Annotate Oauth2 flow initialization parameters in connector specification                                                        |
| 0.1.1   | 2021-09-21 | [6209](https://github.com/airbytehq/airbyte/pull/6209) | Fix bug with pagination for BULK API                                                                                             |
| 0.1.0   | 2021-09-08 | [5619](https://github.com/airbytehq/airbyte/pull/5619) | Salesforce Aitbyte-Native Connector                                                                                              |
