# Salesforce

Setting up the Salesforce source connector involves creating a read-only Salesforce user and configuring the Salesforce connector through the Airbyte UI.

This page guides you through the process of setting up the Salesforce source connector.

## Prerequisites

* [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
* Dedicated Salesforce [user](https://help.salesforce.com/s/articleView?id=adding_new_users.htm&type=5&language=en_US) (optional)
<!-- env:oss -->
* (For Airbyte Open Source) Salesforce [OAuth](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_tokens_scopes.htm&type=5) credentials
<!-- /env:oss -->

## Setup guide

### Step 1: (Optional, Recommended) Create a read-only Salesforce user

While you can set up the Salesforce connector using any Salesforce user with read permission, we recommend creating a dedicated read-only user for Airbyte. This allows you to granularly control the data Airbyte can read.

To create a dedicated read only Salesforce user:

1. [Log into Salesforce](https://login.salesforce.com/) with an admin account.
2. On the top right of the screen, click the gear icon and then click **Setup**.
3. In the left navigation bar, under Administration, click **Users** > **Profiles**. The Profiles page is displayed. Click **New profile**.
4. For Existing Profile, select **Read only**. For Profile Name, enter **Airbyte Read Only User**.
5. Click **Save**. The Profiles page is displayed. Click **Edit**.
6. Scroll down to the **Standard Object Permissions** and **Custom Object Permissions** and enable the **Read** checkbox for objects that you want to replicate via Airbyte.
7. Scroll to the top and click **Save**.
8. On the left side, under Administration, click **Users** > **Users**. The All Users page is displayed. Click **New User**.
9. Fill out the required fields:
    1. For License, select **Salesforce**.
    2. For Profile, select **Airbyte Read Only User**.
    3. For Email, make sure to use an email address that you can access.
10. Click **Save**.
11. Copy the Username and keep it accessible.
12. Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

### Step 2: Set up Salesforce as a Source in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

To set up Salesforce as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Salesforce** from the **Source type** dropdown.
4. For Name, enter a name for the Salesforce connector.
5. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
6. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate the data for last two years.
7. (Optional) In the Salesforce Object filtering criteria section, click **Add**. From the Search criteria dropdown, select the criteria relevant to you. For Search value, add the search terms relevant to you. If this field is blank, Airbyte will replicate all data.
8. Click **Authenticate your account** to authorize your Salesforce account. Airbyte will authenticate the Salesforce account you are already logged in to. Make sure you are logged into the right account.
9. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

To set up Salesforce as a source in Airbyte Open Source:

1. Follow this [walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) with the following modifications:

    1. If your Salesforce URL’s is not in the `X.salesforce.com` format, use your Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`.
    2. When running a curl command, run it with the `-L` option to follow any redirects.
    3. If you [created a read-only user](https://docs.google.com/document/d/1wZR8pz4MRdc2zUculc9IqoF8JxN87U40IqVnTtcqdrI/edit#heading=h.w5v6h7b2a9y4), use the user credentials when logging in to generate OAuth tokens.

2. Navigate to the Airbute Open Source dashboard and follow the same steps as [setting up Salesforce as a source in Airbyte Cloud](#for-airbyte-cloud).
<!-- /env:oss -->

## Supported sync modes

The Salesforce source connector supports the following sync modes:

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* (Recommended)[ Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

### Incremental Deletes Sync

The Salesforce connector retrieves deleted records from Salesforce. For the streams which support it, a deleted record will be marked with the field `isDeleted=true` value.

## Performance considerations

The Salesforce connector is restricted by Salesforce’s [Daily Rate Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm). The connector syncs data until it hits the daily rate limit, then ends the sync early with success status, and starts the next sync from where it left off. Note that picking up from where it ends will work only for incremental sync, which is why we recommend using the [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history) sync mode.

## Supported Objects

The Salesforce connector supports reading both Standard Objects and Custom Objects from Salesforce. Each object is read as a separate stream. See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

Airbyte fetches and handles all the possible and available streams dynamically based on:

* If the authenticated Salesforce user has the Role and Permissions to read and fetch objects

* If the stream has the queryable property set to true. Airbyte can fetch only queryable streams via the API. If you don’t see your object available via Airbyte, check if it is API-accessible to the Salesforce user you authenticated with in Step 2.

**Note:** [BULK API](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm) cannot be used to receive data from the following streams due to Salesforce API limitations. The Salesforce connector syncs them using the REST API which will occasionally cost more of your API quota:

* AcceptedEventRelation
* Attachment
* CaseStatus
* ContractStatus
* DeclinedEventRelation
* FieldSecurityClassification
* KnowledgeArticle
* KnowledgeArticleVersion
* KnowledgeArticleVersionHistory
* KnowledgeArticleViewStat
* KnowledgeArticleVoteStat
* OrderStatus
* PartnerRole
* RecentlyViewed
* ServiceAppointmentStatus
* ShiftStatus
* SolutionStatus
* TaskPriority
* TaskStatus
* UndecidedEventRelation

## Salesforce tutorials

Now that you have set up the Salesforce source connector, check out the following Salesforce tutorials:

* [Replicate Salesforce data to BigQuery](https://airbyte.com/tutorials/replicate-salesforce-data-to-bigquery)
* [Replicate Salesforce and Zendesk data to Keen for unified analytics](https://airbyte.com/tutorials/salesforce-zendesk-analytics)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| 2.0.14  | 2023-05-04 | [25794](https://github.com/airbytehq/airbyte/pull/25794) | Avoid pandas inferring wrong data types by forcing all data type as object                                            |
| 2.0.13  | 2023-04-30 | [25700](https://github.com/airbytehq/airbyte/pull/25700) | Remove pagination and query limits                                                                                               |
| 2.0.12  | 2023-04-25 | [25507](https://github.com/airbytehq/airbyte/pull/25507) | Update API version to 57                                                                                                         |
| 2.0.11  | 2023-04-20 | [25352](https://github.com/airbytehq/airbyte/pull/25352) | Update API version to 53                                                                                                         |
| 2.0.10  | 2023-04-05 | [24888](https://github.com/airbytehq/airbyte/pull/24888) | Add more frequent checkpointing                                                                                                  |
| 2.0.9   | 2023-03-29 | [24660](https://github.com/airbytehq/airbyte/pull/24660) | Set default start_date. Sync for last two years if start date is not present in config                                           |
| 2.0.8   | 2023-03-30 | [24690](https://github.com/airbytehq/airbyte/pull/24690) | Handle rate limit for bulk operations                                                                                            |
| 2.0.7   | 2023-03-14 | [24071](https://github.com/airbytehq/airbyte/pull/24071) | Remove regex pattern for start_date, use format validation instead                                                               |
| 2.0.6   | 2023-03-03 | [22891](https://github.com/airbytehq/airbyte/pull/22891) | Specified date formatting in specification                                                                                       |
| 2.0.5   | 2023-03-01 | [23610](https://github.com/airbytehq/airbyte/pull/23610) | Handle different Salesforce page size for different queries                                                                      |
| 2.0.4   | 2023-02-24 | [22636](https://github.com/airbytehq/airbyte/pull/22636) | Turn on default HttpAvailabilityStrategy for all streams that are not of class BulkSalesforceStream                              |
| 2.0.3   | 2023-02-17 | [23190](https://github.com/airbytehq/airbyte/pull/23190) | In case properties are chunked, fetch primary key in every chunk                                                                 |
| 2.0.2   | 2023-02-13 | [22896](https://github.com/airbytehq/airbyte/pull/22896) | Count the URL length based on encoded params                                                                                     |
| 2.0.1   | 2023-02-08 | [22597](https://github.com/airbytehq/airbyte/pull/22597) | Make multiple requests if a REST stream has too many properties                                                                  |
| 2.0.0   | 2023-02-02 | [22322](https://github.com/airbytehq/airbyte/pull/22322) | Remove `ActivityMetricRollup` stream                                                                                             |
| 1.0.30  | 2023-01-27 | [22016](https://github.com/airbytehq/airbyte/pull/22016) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                      |
| 1.0.29  | 2023-01-05 | [20886](https://github.com/airbytehq/airbyte/pull/20886) | Remove `ActivityMetric` stream                                                                                                   |
| 1.0.28  | 2022-12-29 | [20927](https://github.com/airbytehq/airbyte/pull/20927) | Fix tests; add expected records                                                                                                  |
| 1.0.27  | 2022-11-29 | [19869](https://github.com/airbytehq/airbyte/pull/19869) | Remove `AccountHistory` from unsupported BULK streams                                                                            |
| 1.0.26  | 2022-11-15 | [19286](https://github.com/airbytehq/airbyte/pull/19286) | Bugfix: fallback to REST API if entity is not supported by BULK API                                                              |
| 1.0.25  | 2022-11-13 | [19294](https://github.com/airbytehq/airbyte/pull/19294) | Use the correct encoding for non UTF-8 objects and data                                                                          |
| 1.0.24  | 2022-11-01 | [18799](https://github.com/airbytehq/airbyte/pull/18799) | Update list of unsupported Bulk API objects                                                                                      |
| 1.0.23  | 2022-11-01 | [18753](https://github.com/airbytehq/airbyte/pull/18753) | Add error_display_message for ConnectionError                                                                                    |
| 1.0.22  | 2022-10-12 | [17615](https://github.com/airbytehq/airbyte/pull/17615) | Make paging work, if `cursor_field` is not changed inside one page                                                               |
| 1.0.21  | 2022-10-10 | [17778](https://github.com/airbytehq/airbyte/pull/17778) | Add `EventWhoRelation` to the list of unsupported Bulk API objects.                                                              |
| 1.0.20  | 2022-09-30 | [17453](https://github.com/airbytehq/airbyte/pull/17453) | Check objects that are not supported by the Bulk API (v52.0)                                                                     |
| 1.0.19  | 2022-09-29 | [17314](https://github.com/airbytehq/airbyte/pull/17314) | Fixed bug with decoding response                                                                                                 |
| 1.0.18  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states.                                                                                                    |
| 1.0.17  | 2022-09-23 | [17094](https://github.com/airbytehq/airbyte/pull/17094) | Tune connection check: fetch a list of available streams                                                                         |
| 1.0.16  | 2022-09-21 | [17001](https://github.com/airbytehq/airbyte/pull/17001) | Improve writing file of decode                                                                                                   |
| 1.0.15  | 2022-08-30 | [16086](https://github.com/airbytehq/airbyte/pull/16086) | Improve API type detection                                                                                                       |
| 1.0.14  | 2022-08-29 | [16119](https://github.com/airbytehq/airbyte/pull/16119) | Exclude `KnowledgeArticleVersion` from using bulk API                                                                            |
| 1.0.13  | 2022-08-23 | [15901](https://github.com/airbytehq/airbyte/pull/15901) | Exclude `KnowledgeArticle` from using bulk API                                                                                   |
| 1.0.12  | 2022-08-09 | [15444](https://github.com/airbytehq/airbyte/pull/15444) | Fixed bug when `Bulk Job` was timeout by the connector, but remained running on the server                                       |
| 1.0.11  | 2022-07-07 | [13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field descriptions                                                                                         |
| 1.0.10  | 2022-06-09 | [13658](https://github.com/airbytehq/airbyte/pull/13658) | Correct logic to sync stream larger than page size                                                                               |
| 1.0.9   | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685) | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions                                                     |
| 1.0.8   | 2022-05-04 | [12576](https://github.com/airbytehq/airbyte/pull/12576) | Decode responses as utf-8 and fallback to ISO-8859-1 if needed                                                                   |
| 1.0.7   | 2022-05-03 | [12552](https://github.com/airbytehq/airbyte/pull/12552) | Decode responses as ISO-8859-1 instead of utf-8                                                                                  |
| 1.0.6   | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep                                                          |
| 1.0.5   | 2022-04-25 | [12304](https://github.com/airbytehq/airbyte/pull/12304) | Add `Describe` stream                                                                                                            |
| 1.0.4   | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                                                            |
| 1.0.3   | 2022-04-04 | [11692](https://github.com/airbytehq/airbyte/pull/11692) | Optimised memory usage for `BULK` API calls                                                                                      |
| 1.0.2   | 2022-03-01 | [10751](https://github.com/airbytehq/airbyte/pull/10751) | Fix broken link anchor in connector configuration                                                                                |
| 1.0.1   | 2022-02-27 | [10679](https://github.com/airbytehq/airbyte/pull/10679) | Reorganize input parameter order on the UI                                                                                       |
| 1.0.0   | 2022-02-27 | [10516](https://github.com/airbytehq/airbyte/pull/10516) | Speed up schema discovery by using parallelism                                                                                   |
| 0.1.23  | 2022-02-10 | [10141](https://github.com/airbytehq/airbyte/pull/10141) | Processing of failed jobs                                                                                                        |
| 0.1.22  | 2022-02-02 | [10012](https://github.com/airbytehq/airbyte/pull/10012) | Increase CSV field_size_limit                                                                                                    |
| 0.1.21  | 2022-01-28 | [9499](https://github.com/airbytehq/airbyte/pull/9499)   | If a sync reaches daily rate limit it ends the sync early with success status. Read more in `Performance considerations` section |
| 0.1.20  | 2022-01-26 | [9757](https://github.com/airbytehq/airbyte/pull/9757)   | Parse CSV with "unix" dialect                                                                                                    |
| 0.1.19  | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                                                                                        |
| 0.1.18  | 2022-01-20 | [9478](https://github.com/airbytehq/airbyte/pull/9478)   | Add available stream filtering by `queryable` flag                                                                               |
| 0.1.17  | 2022-01-19 | [9302](https://github.com/airbytehq/airbyte/pull/9302)   | Deprecate API Type parameter                                                                                                     |
| 0.1.16  | 2022-01-18 | [9151](https://github.com/airbytehq/airbyte/pull/9151)   | Fix pagination in REST API streams                                                                                               |
| 0.1.15  | 2022-01-11 | [9409](https://github.com/airbytehq/airbyte/pull/9409)   | Correcting the presence of an extra `else` handler in the error handling                                                         |
| 0.1.14  | 2022-01-11 | [9386](https://github.com/airbytehq/airbyte/pull/9386)   | Handling 400 error, while `sobject` doesn't support `query` or `queryAll` requests                                               |
| 0.1.13  | 2022-01-11 | [8797](https://github.com/airbytehq/airbyte/pull/8797)   | Switched from authSpecification to advanced_auth in specefication                                                                |
| 0.1.12  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871)   | Fix `examples` for new field in specification                                                                                    |
| 0.1.11  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871)   | Add the ability to filter streams by user                                                                                        |
| 0.1.10  | 2021-12-23 | [9005](https://github.com/airbytehq/airbyte/pull/9005)   | Handling 400 error when a stream is not queryable                                                                                |
| 0.1.9   | 2021-12-07 | [8405](https://github.com/airbytehq/airbyte/pull/8405)   | Filter 'null' byte(s) in HTTP responses                                                                                          |
| 0.1.8   | 2021-11-30 | [8191](https://github.com/airbytehq/airbyte/pull/8191)   | Make `start_date` optional and change its format to `YYYY-MM-DD`                                                                 |
| 0.1.7   | 2021-11-24 | [8206](https://github.com/airbytehq/airbyte/pull/8206)   | Handling 400 error when trying to create a job for sync using Bulk API.                                                          |
| 0.1.6   | 2021-11-16 | [8009](https://github.com/airbytehq/airbyte/pull/8009)   | Fix retring of BULK jobs                                                                                                         |
| 0.1.5   | 2021-11-15 | [7885](https://github.com/airbytehq/airbyte/pull/7885)   | Add `Transform` for output records                                                                                               |
| 0.1.4   | 2021-11-09 | [7778](https://github.com/airbytehq/airbyte/pull/7778)   | Fix types for `anyType` fields                                                                                                   |
| 0.1.3   | 2021-11-06 | [7592](https://github.com/airbytehq/airbyte/pull/7592)   | Fix getting `anyType` fields using BULK API                                                                                      |
| 0.1.2   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                        |
| 0.1.1   | 2021-09-21 | [6209](https://github.com/airbytehq/airbyte/pull/6209)   | Fix bug with pagination for BULK API                                                                                             |
| 0.1.0   | 2021-09-08 | [5619](https://github.com/airbytehq/airbyte/pull/5619)   | Salesforce Aitbyte-Native Connector                                                                                              |
