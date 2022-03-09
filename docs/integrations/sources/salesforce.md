# Salesforce

## Overview

The Salesforce source supports both `Full Refresh` and `Incremental` syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

The Connector supports replicating both standard and custom Salesforce objects.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

#### Incremental Deletes Sync
This connector retrieves deleted records from Salesforce. For the streams which support it, a deleted record will be marked with the field `isDeleted=true` value.  

### Performance considerations

The connector is restricted by daily Salesforce rate limiting.
The connector uses as much rate limit as it can every day, then ends the sync early with success status and continues the sync from where it left the next time.
Note that, picking up from where it ends will work only for incremental sync.

## Getting Started (Airbyte Cloud)

#### Sandbox accounts

If you log in using at [https://login.salesforce.com](https://login.salesforce.com), then your account is not a sandbox. If you log in at [https://test.salesforce.com](https://test.salesforce.com) then it's a sandbox. 

If this is Greek to you, then you are likely not using a sandbox account.

### Requirements

* Salesforce Account with Enterprise access or API quota purchased
* Dedicated Salesforce user (optional)

### Setup guide

#### Creating a dedicated read only Salesforce user
While you can setup the Salesforce connector using any user which has read permissions to your account, we recommend creating a dedicated, read-only user for use with Airbyte. This allows you to granularly control the data Airbyte can read. 

To create a dedicated read only Salesforce user: 
1. Login to Salesforce with an admin account
2. On the top right side of the screen, click the "setup" gear icon then click "Setup"
3. Under the "Administration" section on the left side of the screen, click "Users" > "Profiles"
4. Click the "new profile" button
5. Select "Read only" as the value of the "Existing Profile" field, and `Airbyte Read Only User` (or whatever name you prefer) as the profile name
6. click "Save". This should take you to the profiles page. 
7. Click "edit"
8. Scroll down to the "Standard Object Permissions" and "Custom Object Permissions" and enable the "read" checkbox for objects which you would to be able to replicate via Airbyte
9. Scroll to the top and click "Save"
10. Under the "Administration" section on the left side of the screen, click "Users" > "Users". 
11. Click "New User"
12. Fill out the required fields

    a. In the "License" field, select `Salesforce`
    
    b. In the "Profile" field, select `Airbyte Read Only User`
    
    c. In the "Email" field, make sure to use an email address which you can access (this will be required later to verify the account)
13. Click "save"
14. Copy the "Username" field and keep it handy -- you will use it when setting up Airbyte later
15. Login to the email you set in step 12c above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password handy. 
16. With the username and password, you should be ready to setup the Salesforce connector.  
    
#### Configuring the connector in the Airbyte UI
1. Toggle whether your Salesforce account is a Sandbox account or a live account.  
2. Click `Authenticate your Salesforce account` to sign in with Salesforce and authorize your account.
3. Fill in the rest of the details.
4. You should be ready to sync data. 

## Getting started (Airbyte OSS) 
### Requirements
* Salesforce Account with Enterprise access or API quota purchased
* Dedicated read only Salesforce user (optional)
* Salesforce OAuth credentials 

### Setup guide

#### Sandbox accounts
If you log in using at [https://login.salesforce.com](https://login.salesforce.com), then your account is not a sandbox. If you log in at [https://test.salesforce.com](https://test.salesforce.com) then it's a sandbox. 

If this is Greek to you, then you are likely not using a sandbox account.

### Setup guide

#### Read only user
See the [section above](#creating-a-dedicated-read-only-salesforce-user) for creating a read only user. This step is optional.  

#### Salesforce Oauth Credentials
We recommend the following [walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) **while keeping in mind the edits we suggest below** for setting up a Salesforce app that can pull data from Salesforce and locating the credentials you need to provide to Airbyte.

Suggested edits:

1. If your salesforce URL does not take the form `X.salesforce.com`, use your actual Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`. 
2. When running a `curl` command, always run it with the `-L` option to follow any redirects.
3. If you created a read only user, use those credentials when logging in to generate oauth tokens

## Streams

**Note**: The connector supports reading both Standard Objects and Custom Objects from Salesforce. Each object is read as a separate stream. 

See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm). 

We fetch and handle all the possible & available streams dynamically based on:
- User Role & Permissions to read & fetch objects and their data
- Whether or not the stream has the queryable property set to true. Queryable streams are available to be fetched via the API. If you cannot see your object available via Airbyte, please ensure it is API-accessible to the user you used for authenticating into Airbyte  

**Note**: Using the BULK API is not possible to receive data from the following streams due to limitations from the Salesforce API. The connector will sync them via the REST API which will occasionally cost more of your API quota:

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
| 1.0.2 | 2022-03-01 | [10751](https://github.com/airbytehq/airbyte/pull/10751) | Fix broken link anchor in connector configuration |
| 1.0.1 | 2022-02-27 | [10679](https://github.com/airbytehq/airbyte/pull/10679) | Reorganize input parameter order on the UI |
| 1.0.0 | 2022-02-27 | [10516](https://github.com/airbytehq/airbyte/pull/10516) | Speed up schema discovery by using parallelism |
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
