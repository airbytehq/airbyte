# Salesforce

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

<HideInUI>

This page contains the setup guide and reference information for the [Salesforce](https://www.salesforce.com/) source connector.

</HideInUI>

## Prerequisites

- [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
- (Optional, Recommended) Dedicated Salesforce [user](https://help.salesforce.com/s/articleView?id=adding_new_users.htm&type=5&language=en_US)
<!-- env:oss -->
- (For Airbyte Open Source) Salesforce [OAuth](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_tokens_scopes.htm&type=5) credentials
<!-- /env:oss -->

:::tip

To use this connector, you'll need at least the Enterprise edition of Salesforce or the Professional Edition with API access purchased as an add-on. Reference the [Salesforce docs about API access](https://help.salesforce.com/s/articleView?id=000385436&type=1) for more information.

:::

## Setup guide

### Set up Salesforce

### Step 1: (Optional, Recommended) Create a dedicated Salesforce user

Follow the instructions below to create a Minimum Access standard profile and assign custom permission sets to grant the new user the read access needed for data you want to access with Airbyte.

While you can set up the Salesforce connector using any Salesforce user with read permission, we recommend creating a dedicated user with the Minimum Access standard profile for Airbyte. This allows you to granularly control the data Airbyte can read.

Using Permission Sets, you should grant this user read access to the data you want Airbyte to have access to. Learn more about Permission sets by referring to [Salesforce's documentation](https://help.salesforce.com/s/articleView?id=sf.perm_sets_overview.htm&type=5).

[Log in to Salesforce](https://login.salesforce.com/) with an admin account.

#### 1. Create a new User:
-  On the top right of the screen, click the gear icon and then click **Setup**.
-  In the left navigation bar, under Administration, click **Users** > **Users**. Create a new User, entering details for the user's first name, last name, alias, and email. Filling in the email field will auto-populate the username field and nickname.
      - Leave `role` unspecified
      - Select `Salesforce Platform` for the User License
      - Select `Standard Platform User` for Profile.
      - Decide whether to generate a new password and notify the user.
      - Select `save`
#### 2. Create a new Permission Set:
-  Using the left navigation bar, select **Users** > **Permission Sets**
- Click `New` to create a new Permission Set.
- Give your permission set a descriptive label name (e.g., "Airbyte Read Only Access"). The API name will autopopulate based on the label you give the permission set.
- For licence, leave this set to` –None—` and click `save`.
- Now that you see the permission set is created, define the permissions via Object Settings.
   - Click "Object Settings."
   - Select the `Object Name` for each object you want the user to have read-only access to (e.g., Accounts, Contacts, Opportunities).
   - Select “Edit” and check the "Read" permission and uncheck all other permissions (Create, Edit, Delete, etc.).
   - Click `Save`
   - Continue to add read permissions for any objects you want Airbyte to have access to.
#### 3. Assign the Permission Set to the new User
- From the Permission Sets page, click "Manage Assignments" next to the read-only permission set you just created.
- Click "Add Assignments."
- Find and select the user you created in Step 1.
- Click `Assign`

Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

:::info
**Profile vs. Permission Set:** Remember that the user's profile will provide their baseline permissions. The permission set adds or restricts permissions on top of that.
**Object-Level vs. Field-Level Security:** This guide focuses on object-level read-only access. While setting up your permission set, you can stick with object-level security or define more granular controls by scrolling down within each object settings page to select read access for only needed fields.
:::

<!-- env:oss -->

### For Airbyte Open Source: Obtain Salesforce OAuth credentials

If you are using Airbyte Open Source, you will need to obtain the following OAuth credentials to authenticate:

- Client ID
- Client Secret
- Refresh Token

To obtain these credentials, follow [this walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) with the following modifications:

1.  If your Salesforce URL is not in the `X.salesforce.com` format, use your Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`.
2.  When running a curl command, run it with the `-L` option to follow any redirects.
3.  If you created a read-only user, use the user credentials when logging in to generate OAuth tokens.

<!-- /env:oss -->

### Step 2: Set up the Salesforce connector in Airbyte

<!-- env:cloud -->

## For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Salesforce from the Source type dropdown.
4. Enter a name for the Salesforce connector.
5. To authenticate:
   **For Airbyte Cloud**: Click **Authenticate your account** to authorize your Salesforce account. Airbyte will authenticate the Salesforce account you are already logged in to. Please make sure you are logged into the right account.
6. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
7. (Optional) For **Start Date**, use the provided datepicker or enter the date programmatically in either `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` format. The data added on and after this date will be replicated. If this field is left blank, Airbyte will replicate the data for the last two years by default. Please note that timestamps are in [UTC](https://www.utctime.net/).
8. (Optional) In the **Filter Salesforce Object** section, you may choose to target specific data for replication. To do so, click **Add**, then select the relevant criteria from the **Search criteria** dropdown. For **Search value**, add the search terms relevant to you. You may add multiple filters. If no filters are specified, Airbyte will replicate all data.
9. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

## For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Salesforce** from the list of available sources.
4. Enter a **Source name** of your choosing to help you identify this source.
5. To authenticate:
   **For Airbyte Open Source**: Enter your Client ID, Client Secret, and Refresh Token.
6. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
7. (Optional) For **Start Date**, use the provided datepicker or enter the date programmatically in either `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` format. The data added on and after this date will be replicated. If this field is left blank, Airbyte will replicate the data for the last two years by default. Please note that timestamps are in [UTC](https://www.utctime.net/).
8. (Optional) In the **Filter Salesforce Object** section, you may choose to target specific data for replication. To do so, click **Add**, then select the relevant criteria from the **Search criteria** dropdown. For **Search value**, add the search terms relevant to you. You may add multiple filters. If no filters are specified, Airbyte will replicate all data.
9. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Salesforce source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- (Recommended)[ Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)
- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

The Salesforce connector supports reading both Standard Objects and Custom Objects from Salesforce. Each object is read as a separate stream. See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

Airbyte allows exporting all available Salesforce objects dynamically based on:

- If the authenticated Salesforce user has the Role and Permissions to read and fetch objects. This would be set as part of the Permission Set you assign to the Airbyte user. See [Step 1](#step-1-optional-recommended-create-a-dedicated-salesforce-user) for more information.
- If the Salesforce object has the queryable property set to true. Airbyte can only fetch objects which are queryable. If you don’t see an object available via Airbyte, and it is queryable, check if it is API-accessible to the Salesforce user you authenticated with.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Salesforce connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Salesforce connector is restricted by Salesforce’s [Daily Rate Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm). The connector syncs data until it hits the daily rate limit, then ends the sync early with success status, and starts the next sync from where it left off. Note that picking up from where it ends will work only for incremental sync, which is why we recommend using the [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) sync mode.

#### A note on the BULK API vs REST API and their limitations

## Syncing Formula Fields

The Salesforce connector syncs formula field outputs from Salesforce. If the formula of a field changes in Salesforce and no other field on the record is updated, you will need to reset the stream and sync a historical backfill to pull in all the updated values of the field.

## Syncing Deletes

The Salesforce connector supports retrieving deleted records from the Salesforce recycle bin. For the streams which support it, a deleted record will be marked with `isDeleted=true`. To find out more about how Salesforce manages records in the recycle bin, please visit their [docs](https://help.salesforce.com/s/articleView?id=sf.home_delete.htm&type=5).

## Usage of the BULK API vs REST API

Salesforce allows extracting data using either the [BULK API](https://developer.salesforce.com/docs/atlas.en-us.236.0.api_asynch.meta/api_asynch/asynch_api_intro.htm) or [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm). To achieve fast performance, Salesforce recommends using the BULK API for extracting larger amounts of data (more than 2,000 records). For this reason, the Salesforce connector uses the BULK API by default to extract any Salesforce objects, unless any of the following conditions are met:

- The Salesforce object has columns which are unsupported by the BULK API, like columns with a `base64` or `complexvalue` type
- The Salesforce object is not supported by BULK API. In this case we sync the objects via the REST API which will occasionally cost more of your API quota. This includes the following objects:
  - AcceptedEventRelation
  - Attachment
  - CaseStatus
  - ContractStatus
  - DeclinedEventRelation
  - FieldSecurityClassification
  - KnowledgeArticle
  - KnowledgeArticleVersion
  - KnowledgeArticleVersionHistory
  - KnowledgeArticleViewStat
  - KnowledgeArticleVoteStat
  - OrderStatus
  - PartnerRole
  - RecentlyViewed
  - ServiceAppointmentStatus
  - ShiftStatus
  - SolutionStatus
  - TaskPriority
  - TaskStatus
  - UndecidedEventRelation

More information on the differences between various Salesforce APIs can be found [here](https://help.salesforce.com/s/articleView?id=sf.integrate_what_is_api.htm&type=5).

:::info Force Using Bulk API
If you set the `Force Use Bulk API` option to `true`, the connector will ignore unsupported properties and sync Stream using BULK API.
:::

### Troubleshooting

#### Tutorials

Now that you have set up the Salesforce source connector, check out the following Salesforce tutorials:

- [Replicate Salesforce data to BigQuery](https://airbyte.com/tutorials/replicate-salesforce-data-to-bigquery)
- [Replicate Salesforce and Zendesk data to Keen for unified analytics](https://airbyte.com/tutorials/salesforce-zendesk-analytics)

* Check out common troubleshooting issues for the Salesforce source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                             |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| 2.6.5 | 2025-02-20 | [54178](https://github.com/airbytehq/airbyte/pull/54178) | Promoting release candidate 2.6.5-rc.1 to a main version. |
| 2.6.5-rc.1 | 2025-02-18 | [53229](https://github.com/airbytehq/airbyte/pull/53229) | Upgrade to API v62.0 |
| 2.6.4 | 2025-01-11 | [48635](https://github.com/airbytehq/airbyte/pull/48635) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.6.3 | 2024-11-05 | [46835](https://github.com/airbytehq/airbyte/pull/46835) | Update dependencies |
| 2.6.2 | 2024-10-10 | [](https://github.com/airbytehq/airbyte/pull/) | Bump minimum CDK to 5.10.2 |
| 2.6.1 | 2024-10-05 | [46436](https://github.com/airbytehq/airbyte/pull/46436) | Update dependencies, including CDK fix in v5.10.2 |
| 2.6.0 | 2024-10-02 | [45678](https://github.com/airbytehq/airbyte/pull/45678) | Have bulk streams use CDK components |
| 2.5.34 | 2024-09-28 | [46187](https://github.com/airbytehq/airbyte/pull/46187) | Update dependencies |
| 2.5.33 | 2024-09-21 | [45779](https://github.com/airbytehq/airbyte/pull/45779) | Update dependencies |
| 2.5.32 | 2024-09-14 | [45579](https://github.com/airbytehq/airbyte/pull/45579) | Update dependencies |
| 2.5.31 | 2024-09-07 | [45329](https://github.com/airbytehq/airbyte/pull/45329) | Update dependencies |
| 2.5.30 | 2024-08-31 | [44959](https://github.com/airbytehq/airbyte/pull/44959) | Update dependencies |
| 2.5.29 | 2024-08-24 | [44747](https://github.com/airbytehq/airbyte/pull/44747) | Update dependencies |
| 2.5.28 | 2024-08-17 | [44327](https://github.com/airbytehq/airbyte/pull/44327) | Update dependencies |
| 2.5.27 | 2024-08-12 | [43732](https://github.com/airbytehq/airbyte/pull/43732) | Update dependencies |
| 2.5.26 | 2024-08-10 | [43673](https://github.com/airbytehq/airbyte/pull/43673) | Update dependencies |
| 2.5.25 | 2024-08-03 | [43211](https://github.com/airbytehq/airbyte/pull/43211) | Update dependencies |
| 2.5.24 | 2024-07-27 | [42685](https://github.com/airbytehq/airbyte/pull/42685) | Update dependencies |
| 2.5.23 | 2024-07-20 | [42166](https://github.com/airbytehq/airbyte/pull/42166) | Update dependencies |
| 2.5.22 | 2024-07-13 | [41752](https://github.com/airbytehq/airbyte/pull/41752) | Update dependencies |
| 2.5.21 | 2024-07-10 | [41529](https://github.com/airbytehq/airbyte/pull/41529) | Update dependencies |
| 2.5.20 | 2024-07-09 | [41255](https://github.com/airbytehq/airbyte/pull/41255) | Update dependencies |
| 2.5.19 | 2024-07-08 | [41043](https://github.com/airbytehq/airbyte/pull/41043) | Use the latest `CDK` version possible |
| 2.5.18 | 2024-07-06 | [40835](https://github.com/airbytehq/airbyte/pull/40835) | Update dependencies |
| 2.5.17 | 2024-06-25 | [40329](https://github.com/airbytehq/airbyte/pull/40329) | Update dependencies |
| 2.5.16 | 2024-06-21 | [39927](https://github.com/airbytehq/airbyte/pull/39927) | Update dependencies |
| 2.5.15 | 2024-06-16 | [39517](https://github.com/airbytehq/airbyte/pull/39517) | Salesforce refactor: add CheckpointMixin for state management |
| 2.5.14 | 2024-06-06 | [39269](https://github.com/airbytehq/airbyte/pull/39269) | [autopull] Upgrade base image to v1.2.2 |
| 2.5.13 | 2024-05-23 | [38563](https://github.com/airbytehq/airbyte/pull/38563) | Use HttpClient to perform HTTP requests for bulk, authentication and schema discovery |
| 2.5.12 | 2024-05-16 | [38255](https://github.com/airbytehq/airbyte/pull/38255) | Replace AirbyteLogger with logging.Logger |
| 2.5.11 | 2024-05-09 | [38205](https://github.com/airbytehq/airbyte/pull/38205) | Use new delete method of HttpMocker for test_bulk_stream |
| 2.5.10 | 2024-05-09 | [38065](https://github.com/airbytehq/airbyte/pull/38065) | Replace deprecated authentication mechanism to up-to-date one |
| 2.5.9 | 2024-05-02 | [37749](https://github.com/airbytehq/airbyte/pull/37749) | Adding mock server tests for bulk streams |
| 2.5.8 | 2024-04-30 | [37340](https://github.com/airbytehq/airbyte/pull/37340) | Source Salesforce: reduce info logs |
| 2.5.7 | 2024-04-24 | [36657](https://github.com/airbytehq/airbyte/pull/36657) | Schema descriptions |
| 2.5.6 | 2024-04-19 | [37448](https://github.com/airbytehq/airbyte/pull/37448) | Ensure AirbyteTracedException in concurrent CDK are emitted with the right type |
| 2.5.5   | 2024-04-18 | [37392](https://github.com/airbytehq/airbyte/pull/37419) | Ensure python return code != 0 in case of error                                                                                     |
| 2.5.4   | 2024-04-18 | [37392](https://github.com/airbytehq/airbyte/pull/37392) | Update CDK version to have partitioned state fix                                                                                    |
| 2.5.3   | 2024-04-17 | [37376](https://github.com/airbytehq/airbyte/pull/37376) | Improve rate limit error message during check command                                                                               |
| 2.5.2   | 2024-04-15 | [37105](https://github.com/airbytehq/airbyte/pull/37105) | Raise error when schema generation fails                                                                                            |
| 2.5.1   | 2024-04-11 | [37001](https://github.com/airbytehq/airbyte/pull/37001) | Update airbyte-cdk to flush print buffer for every message                                                                          |
| 2.5.0   | 2024-04-11 | [36942](https://github.com/airbytehq/airbyte/pull/36942) | Move Salesforce to partitioned state in order to avoid stuck syncs                                                                  |
| 2.4.4   | 2024-04-08 | [36901](https://github.com/airbytehq/airbyte/pull/36901) | Upgrade CDK for empty internal_message empty when ExceptionWithDisplayMessage raised                                                |
| 2.4.3   | 2024-04-08 | [36885](https://github.com/airbytehq/airbyte/pull/36885) | Add missing retry on REST API                                                                                                       |
| 2.4.2   | 2024-04-05 | [36862](https://github.com/airbytehq/airbyte/pull/36862) | Upgrade CDK for updated error messaging regarding missing streams                                                                   |
| 2.4.1   | 2024-04-03 | [36385](https://github.com/airbytehq/airbyte/pull/36385) | Retry HTTP requests and jobs on various cases                                                                                       |
| 2.4.0   | 2024-03-12 | [35978](https://github.com/airbytehq/airbyte/pull/35978) | Upgrade CDK to start emitting record counts with state and full refresh state                                                       |
| 2.3.3   | 2024-03-04 | [35791](https://github.com/airbytehq/airbyte/pull/35791) | Fix memory leak (OOM)                                                                                                               |
| 2.3.2   | 2024-02-19 | [35421](https://github.com/airbytehq/airbyte/pull/35421) | Add Stream Slice Step option to specification                                                                                       |
| 2.3.1   | 2024-02-12 | [35147](https://github.com/airbytehq/airbyte/pull/35147) | Manage dependencies with Poetry.                                                                                                    |
| 2.3.0   | 2023-12-15 | [33522](https://github.com/airbytehq/airbyte/pull/33522) | Sync streams concurrently in all sync modes                                                                                         |
| 2.2.2   | 2024-01-04 | [33936](https://github.com/airbytehq/airbyte/pull/33936) | Prepare for airbyte-lib                                                                                                             |
| 2.2.1   | 2023-12-12 | [33342](https://github.com/airbytehq/airbyte/pull/33342) | Added new ContentDocumentLink stream                                                                                                |
| 2.2.0   | 2023-12-12 | [33350](https://github.com/airbytehq/airbyte/pull/33350) | Sync streams concurrently on full refresh                                                                                           |
| 2.1.6   | 2023-11-28 | [32535](https://github.com/airbytehq/airbyte/pull/32535) | Run full refresh syncs concurrently                                                                                                 |
| 2.1.5   | 2023-10-18 | [31543](https://github.com/airbytehq/airbyte/pull/31543) | Base image migration: remove Dockerfile and use the python-connector-base image                                                     |
| 2.1.4   | 2023-08-17 | [29538](https://github.com/airbytehq/airbyte/pull/29538) | Fix encoding guess                                                                                                                  |
| 2.1.3   | 2023-08-17 | [29500](https://github.com/airbytehq/airbyte/pull/29500) | handle expired refresh token error                                                                                                  |
| 2.1.2   | 2023-08-10 | [28781](https://github.com/airbytehq/airbyte/pull/28781) | Fix pagination for BULK API jobs; Add option to force use BULK API                                                                  |
| 2.1.1   | 2023-07-06 | [28021](https://github.com/airbytehq/airbyte/pull/28021) | Several Vulnerabilities Fixes; switched to use alpine instead of slim, CVE-2022-40897, CVE-2023-29383, CVE-2023-31484, CVE-2016-2781 |
| 2.1.0   | 2023-06-26 | [27726](https://github.com/airbytehq/airbyte/pull/27726) | License Update: Elv2                                                                                                                |
| 2.0.14  | 2023-05-04 | [25794](https://github.com/airbytehq/airbyte/pull/25794) | Avoid pandas inferring wrong data types by forcing all data type as object                                                          |
| 2.0.13  | 2023-04-30 | [25700](https://github.com/airbytehq/airbyte/pull/25700) | Remove pagination and query limits                                                                                                  |
| 2.0.12  | 2023-04-25 | [25507](https://github.com/airbytehq/airbyte/pull/25507) | Update API version to 57                                                                                                            |
| 2.0.11  | 2023-04-20 | [25352](https://github.com/airbytehq/airbyte/pull/25352) | Update API version to 53                                                                                                            |
| 2.0.10  | 2023-04-05 | [24888](https://github.com/airbytehq/airbyte/pull/24888) | Add more frequent checkpointing                                                                                                     |
| 2.0.9   | 2023-03-29 | [24660](https://github.com/airbytehq/airbyte/pull/24660) | Set default start_date. Sync for last two years if start date is not present in config                                              |
| 2.0.8   | 2023-03-30 | [24690](https://github.com/airbytehq/airbyte/pull/24690) | Handle rate limit for bulk operations                                                                                               |
| 2.0.7   | 2023-03-14 | [24071](https://github.com/airbytehq/airbyte/pull/24071) | Remove regex pattern for start_date, use format validation instead                                                                  |
| 2.0.6   | 2023-03-03 | [22891](https://github.com/airbytehq/airbyte/pull/22891) | Specified date formatting in specification                                                                                          |
| 2.0.5   | 2023-03-01 | [23610](https://github.com/airbytehq/airbyte/pull/23610) | Handle different Salesforce page size for different queries                                                                         |
| 2.0.4   | 2023-02-24 | [22636](https://github.com/airbytehq/airbyte/pull/22636) | Turn on default HttpAvailabilityStrategy for all streams that are not of class BulkSalesforceStream                                 |
| 2.0.3   | 2023-02-17 | [23190](https://github.com/airbytehq/airbyte/pull/23190) | In case properties are chunked, fetch primary key in every chunk                                                                    |
| 2.0.2   | 2023-02-13 | [22896](https://github.com/airbytehq/airbyte/pull/22896) | Count the URL length based on encoded params                                                                                        |
| 2.0.1   | 2023-02-08 | [22597](https://github.com/airbytehq/airbyte/pull/22597) | Make multiple requests if a REST stream has too many properties                                                                     |
| 2.0.0   | 2023-02-02 | [22322](https://github.com/airbytehq/airbyte/pull/22322) | Remove `ActivityMetricRollup` stream                                                                                                |
| 1.0.30  | 2023-01-27 | [22016](https://github.com/airbytehq/airbyte/pull/22016) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                         |
| 1.0.29  | 2023-01-05 | [20886](https://github.com/airbytehq/airbyte/pull/20886) | Remove `ActivityMetric` stream                                                                                                      |
| 1.0.28  | 2022-12-29 | [20927](https://github.com/airbytehq/airbyte/pull/20927) | Fix tests; add expected records                                                                                                     |
| 1.0.27  | 2022-11-29 | [19869](https://github.com/airbytehq/airbyte/pull/19869) | Remove `AccountHistory` from unsupported BULK streams                                                                               |
| 1.0.26  | 2022-11-15 | [19286](https://github.com/airbytehq/airbyte/pull/19286) | Bugfix: fallback to REST API if entity is not supported by BULK API                                                                 |
| 1.0.25  | 2022-11-13 | [19294](https://github.com/airbytehq/airbyte/pull/19294) | Use the correct encoding for non UTF-8 objects and data                                                                             |
| 1.0.24  | 2022-11-01 | [18799](https://github.com/airbytehq/airbyte/pull/18799) | Update list of unsupported Bulk API objects                                                                                         |
| 1.0.23  | 2022-11-01 | [18753](https://github.com/airbytehq/airbyte/pull/18753) | Add error_display_message for ConnectionError                                                                                       |
| 1.0.22  | 2022-10-12 | [17615](https://github.com/airbytehq/airbyte/pull/17615) | Make paging work, if `cursor_field` is not changed inside one page                                                                  |
| 1.0.21  | 2022-10-10 | [17778](https://github.com/airbytehq/airbyte/pull/17778) | Add `EventWhoRelation` to the list of unsupported Bulk API objects.                                                                 |
| 1.0.20  | 2022-09-30 | [17453](https://github.com/airbytehq/airbyte/pull/17453) | Check objects that are not supported by the Bulk API (v52.0)                                                                        |
| 1.0.19  | 2022-09-29 | [17314](https://github.com/airbytehq/airbyte/pull/17314) | Fixed bug with decoding response                                                                                                    |
| 1.0.18  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream states.                                                                                                       |
| 1.0.17  | 2022-09-23 | [17094](https://github.com/airbytehq/airbyte/pull/17094) | Tune connection check: fetch a list of available streams                                                                            |
| 1.0.16  | 2022-09-21 | [17001](https://github.com/airbytehq/airbyte/pull/17001) | Improve writing file of decode                                                                                                      |
| 1.0.15  | 2022-08-30 | [16086](https://github.com/airbytehq/airbyte/pull/16086) | Improve API type detection                                                                                                          |
| 1.0.14  | 2022-08-29 | [16119](https://github.com/airbytehq/airbyte/pull/16119) | Exclude `KnowledgeArticleVersion` from using bulk API                                                                               |
| 1.0.13  | 2022-08-23 | [15901](https://github.com/airbytehq/airbyte/pull/15901) | Exclude `KnowledgeArticle` from using bulk API                                                                                      |
| 1.0.12  | 2022-08-09 | [15444](https://github.com/airbytehq/airbyte/pull/15444) | Fixed bug when `Bulk Job` was timeout by the connector, but remained running on the server                                          |
| 1.0.11  | 2022-07-07 | [13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field descriptions                                                                                            |
| 1.0.10  | 2022-06-09 | [13658](https://github.com/airbytehq/airbyte/pull/13658) | Correct logic to sync stream larger than page size                                                                                  |
| 1.0.9   | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685) | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions                                                        |
| 1.0.8   | 2022-05-04 | [12576](https://github.com/airbytehq/airbyte/pull/12576) | Decode responses as utf-8 and fallback to ISO-8859-1 if needed                                                                      |
| 1.0.7   | 2022-05-03 | [12552](https://github.com/airbytehq/airbyte/pull/12552) | Decode responses as ISO-8859-1 instead of utf-8                                                                                     |
| 1.0.6   | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep                                                             |
| 1.0.5   | 2022-04-25 | [12304](https://github.com/airbytehq/airbyte/pull/12304) | Add `Describe` stream                                                                                                               |
| 1.0.4   | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                                                               |
| 1.0.3   | 2022-04-04 | [11692](https://github.com/airbytehq/airbyte/pull/11692) | Optimised memory usage for `BULK` API calls                                                                                         |
| 1.0.2   | 2022-03-01 | [10751](https://github.com/airbytehq/airbyte/pull/10751) | Fix broken link anchor in connector configuration                                                                                   |
| 1.0.1   | 2022-02-27 | [10679](https://github.com/airbytehq/airbyte/pull/10679) | Reorganize input parameter order on the UI                                                                                          |
| 1.0.0   | 2022-02-27 | [10516](https://github.com/airbytehq/airbyte/pull/10516) | Speed up schema discovery by using parallelism                                                                                      |
| 0.1.23  | 2022-02-10 | [10141](https://github.com/airbytehq/airbyte/pull/10141) | Processing of failed jobs                                                                                                           |
| 0.1.22  | 2022-02-02 | [10012](https://github.com/airbytehq/airbyte/pull/10012) | Increase CSV field_size_limit                                                                                                       |
| 0.1.21  | 2022-01-28 | [9499](https://github.com/airbytehq/airbyte/pull/9499)   | If a sync reaches daily rate limit it ends the sync early with success status. Read more in `Performance considerations` section    |
| 0.1.20  | 2022-01-26 | [9757](https://github.com/airbytehq/airbyte/pull/9757)   | Parse CSV with "unix" dialect                                                                                                       |
| 0.1.19  | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                                                                                           |
| 0.1.18  | 2022-01-20 | [9478](https://github.com/airbytehq/airbyte/pull/9478)   | Add available stream filtering by `queryable` flag                                                                                  |
| 0.1.17  | 2022-01-19 | [9302](https://github.com/airbytehq/airbyte/pull/9302)   | Deprecate API Type parameter                                                                                                        |
| 0.1.16  | 2022-01-18 | [9151](https://github.com/airbytehq/airbyte/pull/9151)   | Fix pagination in REST API streams                                                                                                  |
| 0.1.15  | 2022-01-11 | [9409](https://github.com/airbytehq/airbyte/pull/9409)   | Correcting the presence of an extra `else` handler in the error handling                                                            |
| 0.1.14  | 2022-01-11 | [9386](https://github.com/airbytehq/airbyte/pull/9386)   | Handling 400 error, while `sobject` doesn't support `query` or `queryAll` requests                                                  |
| 0.1.13  | 2022-01-11 | [8797](https://github.com/airbytehq/airbyte/pull/8797)   | Switched from authSpecification to advanced_auth in specefication                                                                   |
| 0.1.12  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871)   | Fix `examples` for new field in specification                                                                                       |
| 0.1.11  | 2021-12-23 | [8871](https://github.com/airbytehq/airbyte/pull/8871)   | Add the ability to filter streams by user                                                                                           |
| 0.1.10  | 2021-12-23 | [9005](https://github.com/airbytehq/airbyte/pull/9005)   | Handling 400 error when a stream is not queryable                                                                                   |
| 0.1.9   | 2021-12-07 | [8405](https://github.com/airbytehq/airbyte/pull/8405)   | Filter 'null' byte(s) in HTTP responses                                                                                             |
| 0.1.8   | 2021-11-30 | [8191](https://github.com/airbytehq/airbyte/pull/8191)   | Make `start_date` optional and change its format to `YYYY-MM-DD`                                                                    |
| 0.1.7   | 2021-11-24 | [8206](https://github.com/airbytehq/airbyte/pull/8206)   | Handling 400 error when trying to create a job for sync using Bulk API.                                                             |
| 0.1.6   | 2021-11-16 | [8009](https://github.com/airbytehq/airbyte/pull/8009)   | Fix retring of BULK jobs                                                                                                            |
| 0.1.5   | 2021-11-15 | [7885](https://github.com/airbytehq/airbyte/pull/7885)   | Add `Transform` for output records                                                                                                  |
| 0.1.4   | 2021-11-09 | [7778](https://github.com/airbytehq/airbyte/pull/7778)   | Fix types for `anyType` fields                                                                                                      |
| 0.1.3   | 2021-11-06 | [7592](https://github.com/airbytehq/airbyte/pull/7592)   | Fix getting `anyType` fields using BULK API                                                                                         |
| 0.1.2   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                           |
| 0.1.1   | 2021-09-21 | [6209](https://github.com/airbytehq/airbyte/pull/6209)   | Fix bug with pagination for BULK API                                                                                                |
| 0.1.0   | 2021-09-08 | [5619](https://github.com/airbytehq/airbyte/pull/5619)   | Salesforce Aitbyte-Native Connector                                                                                                 |

</details>

</HideInUI>
