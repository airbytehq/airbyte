# Intercom

<HideInUI>

This page contains the setup guide and reference information for the [Intercom](https://developers.intercom.com/) source connector.

</HideInUI>

## Prerequisites

- An Intercom account with the data you want to replicate.
- An Intercom app with the required permissions. The connector needs read access to the data you want to sync. At minimum, grant these permissions in the [Developer Hub](https://app.intercom.com/a/apps/_/developer-hub):
  - **Read and list users and companies**—required for Companies, Company Segments, Company Attributes, Contact Attributes, Contacts, Segments, and Teams.
  - **Read conversations**—required for Conversations and Conversation Parts.
  - **Read admins**—required for Admins.
  - **Read admin activity logs**—required for Activity Logs.
  - **Read tags**—required for Tags.
  - **Read Tickets**—required for Tickets. This permission is optional: if it is not granted, the Tickets stream is silently skipped during syncs.
- A **Start date** in UTC format (`YYYY-MM-DDTHH:mm:ssZ`). Only data created on or after this date is replicated.

## Setup guide

### Set up Intercom

<!-- env:oss -->

### Obtain an Intercom access token (Airbyte Open Source)

To authenticate the connector in **Airbyte Open Source**, you need an access token. Follow the steps below to create an Intercom app and generate the token. For more information on Intercom's authentication flow, refer to the [official documentation](https://developers.intercom.com/docs/build-an-integration/learn-more/authentication).

1. Log in to your Intercom account and navigate to the [Developer Hub](https://developers.intercom.com/).
2. Click **Your apps** in the top-right corner, then click **New app**.
3. Choose an **App name**, select your Workspace from the dropdown, and click **Create app**.
4. To set the appropriate permissions, from the **Authentication** tab, click **Edit** in the top right corner and check the permissions you want to grant to the app. Grant only **read** permissions (not **write**). Click **Save** when you are finished.
5. Under the **Access token** header, you will be prompted to regenerate your access token. Follow the instructions to do so, and copy the new token.

<!-- /env:oss -->

### Set up the Intercom connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Intercom** from the Source type dropdown.
4. Enter a name for the Intercom connector.
5. To authenticate:

<!-- env:cloud -->

<!-- env:oss -->
#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Intercom** from the Source type dropdown.
4. Enter a name for the Intercom connector.
<!-- /env:oss -->

- For **Airbyte Cloud**, click **Authenticate your Intercom account**. When the pop-up appears, select the appropriate workspace from the dropdown and click **Authorize access**.
  <!-- /env:cloud -->
  <!-- env:oss -->
- For **Airbyte Open Source**, enter your access token to authenticate your account.
<!-- /env:oss -->

6. For **Start date**, use the provided datepicker or enter a UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ`. Only data created on or after this date is replicated.
7. Optionally, configure **Lookback window** to re-sync records updated within the specified number of days before the current cursor position. This helps capture late-arriving updates. The default is `0` (no lookback).
8. Optionally, configure **Activity logs stream slice step size** to control how many days of activity log data the connector fetches per request. The default is `30` days. Lower this value if you experience timeouts on the Activity Logs stream.
9. Optionally, configure **Num Workers** to set the number of worker threads for concurrent stream processing. The default is `10` (max `40`). Increase this to speed up syncs for workspaces with large volumes of conversations.
10. Optionally, configure **API Rate Limit** to set the effective API request budget per minute. The default is `9500` (95% of the standard 10,000/min Intercom limit). If your workspace has a higher rate limit (e.g. 150,000/min), set this to ~95% of that value to leverage your full API throughput.
11. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Intercom source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

The Intercom source connector supports the following streams:

- [Activity Logs](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/admins/listactivitylogs) \(Incremental\)
- [Admins](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/admins/listadmins) \(Full table\)
- [Companies](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/companies) \(Incremental\)
  - [Company Segments](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/companies/listattachedsegmentsforcompanies) \(Incremental\)
- [Company Attributes](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/data-attributes/listdataattributes) \(Full table\)
- [Contact Attributes](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/data-attributes/listdataattributes) \(Full table\)
- [Contacts](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/contacts/searchcontacts) \(Incremental\)
- [Conversations](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/conversations/searchconversations) \(Incremental\)
  - [Conversation Parts](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/conversations/retrieveconversation) \(Incremental\)
- [Segments](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/segments/listsegments) \(Incremental\)
- [Tags](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/tags/listtags) \(Full table\)
- [Teams](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/teams/listteams) \(Full table\)
- [Tickets](https://developers.intercom.com/docs/references/2.11/rest-api/api.intercom.io/tickets/searchtickets) \(Incremental\)

## Performance considerations

The connector is restricted by normal Intercom [rate limits](https://developers.intercom.com/docs/references/rest-api/errors/rate-limiting). The default rate limit is 1,000 API calls per minute for public apps and 10,000 API calls per minute for private apps, with a workspace-level cap of 25,000 API calls per minute. The connector monitors the `X-RateLimit-Remaining` header and proactively throttles itself before hitting the API rate limit, trading sync speed for stability. If the API returns a `429 Too Many Requests` response, the connector retries automatically.

The connector uses an **API Rate Limit** setting (default: `9500` requests per minute) to control its request budget. A per-10-second window is derived automatically (`api_rate_limit / 6`). If your Intercom workspace has an elevated rate limit (e.g. 150,000/min), increase this value to allow the connector to use your full API throughput.

The connector also supports configurable **concurrency** via the **Num Workers** setting (default: `10`, max: `40`). This controls how many partition slices are processed in parallel, which is especially beneficial for substream-based streams like `conversation_parts` and `company_segments`.

The connector should not run into rate limit issues under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see rate limit errors that are not automatically retried.

## Troubleshooting and limitations

### Companies and Company Segments use client-side incremental sync

The Companies and Company Segments streams rely on the [Scroll over all companies](https://developers.intercom.com/docs/references/rest-api/api.intercom.io/companies/scrolloverallcompanies) endpoint, which does not support server-side datetime filtering. Incremental sync for these streams works by fetching all records from the API and filtering locally, emitting only the records that are newer than the last sync checkpoint.

This means that even if you only need one day of new data, the connector must read all company records from the beginning before it can identify and emit the new ones. For workspaces with a large number of companies, this can result in long sync times.

### Only one scroll can be open per app at a time

The Intercom API allows only one company scroll to be open per app at a time. If a second scroll request is made while one is already active, the API returns a `400` error with the message "scroll already exists for this workspace." The connector retries this error automatically with a one-minute backoff, since scrolls expire after one minute of inactivity.

To prevent conflicts, the connector blocks simultaneous reads from the Companies endpoint. If you run multiple connections that sync the Companies or Company Segments streams from the same Intercom workspace, the connector queues the reads so only one scroll is active at a time.

### Recommendation for reducing sync times

Because these streams must read all records on every sync, syncing Companies and Company Segments alongside other streams in the same connection can increase the total sync duration for that connection. To avoid this, sync the Companies and Company Segments streams in a separate connection from your other Intercom streams.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version      | Date       | Pull Request                                             | Subject                                                                                                                              |
|:-------------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| 0.13.22 | 2026-04-28 | [70464](https://github.com/airbytehq/airbyte/pull/70464) | Update dependencies |
| 0.13.21 | 2026-04-22 | [76847](https://github.com/airbytehq/airbyte/pull/76847) | Update CDK to 7.17.3 |
| 0.13.20 | 2026-04-14 | [76316](https://github.com/airbytehq/airbyte/pull/76316) | Promote 0.13.20-rc.1 to stable and disable progressive rollout |
| 0.13.20-rc.1 | 2026-04-10 | [73717](https://github.com/airbytehq/airbyte/pull/73717) | Add configurable concurrency (`num_workers`), configurable API rate limit (`api_rate_limit`), HTTPAPIBudget, and ErrorHandlerWithRateLimiter for conversation_parts |
| 0.13.19 | 2026-04-09 | [76182](https://github.com/airbytehq/airbyte/pull/76182) | Promote 0.13.19-rc.1 to stable and disable progressive rollout |
| 0.13.19-rc.1 | 2026-04-08 | [76122](https://github.com/airbytehq/airbyte/pull/76122) | Increase HTTP connection pool size |
| 0.13.18 | 2026-04-06 | [75899](https://github.com/airbytehq/airbyte/pull/75899) | Update CDK to 7.15.0 |
| 0.13.17 | 2026-03-30 | [75575](https://github.com/airbytehq/airbyte/pull/75575) | Add `oauth_connector_input_specification` for declarative OAuth |
| 0.13.16 | 2026-03-24 | [75419](https://github.com/airbytehq/airbyte/pull/75419) | Promote 0.13.16-rc.6 to GA — includes CDK 7.13.0 upgrade, block_simultaneous_read for companies, rate limiter fix, step size/end_datetime for incremental streams, and heartbeat timeout bump |
| 0.13.16-rc.6 | 2026-03-19 | [75216](https://github.com/airbytehq/airbyte/pull/75216) | Bump CDK base image to 7.13.0 (includes block_simultaneous_read support and cursor field fix) |
| 0.13.16-rc.5 | 2026-03-11 | [71141](https://github.com/airbytehq/airbyte/pull/71141) | Block simultaneous reading from companies endpoint |
| 0.13.16-rc.4 | 2026-03-03 | [74143](https://github.com/airbytehq/airbyte/pull/74143) | fix(source-intercom): fix UnboundLocalError in rate limiter when response is not available |
| 0.13.16-rc.3 | 2026-03-03 | [72955](https://github.com/airbytehq/airbyte/pull/72955) | fix(source-intercom): add step size and end_datetime to contacts, conversations, and activity_logs streams |
| 0.13.16-rc.2 | 2026-02-18 | [73635](https://github.com/airbytehq/airbyte/pull/73635) | fix(source-intercom): bump heartbeat timeout from 6h to 9h |
| 0.13.16-rc.1 | 2025-12-11 | [70335](https://github.com/airbytehq/airbyte/pull/70335) | Fix pagination on companies stream |
| 0.13.15 | 2025-11-25 | [69563](https://github.com/airbytehq/airbyte/pull/69563) | Update dependencies |
| 0.13.14 | 2025-11-19 | [69306](https://github.com/airbytehq/airbyte/pull/69306) | Update custom IntercomScrollRetriever to not use deprecated stream_state parameter |
| 0.13.13 | 2025-10-29 | [68767](https://github.com/airbytehq/airbyte/pull/68767) | Update dependencies |
| 0.13.12 | 2025-10-21 | [68477](https://github.com/airbytehq/airbyte/pull/68477) | Update dependencies |
| 0.13.11 | 2025-10-14 | [67933](https://github.com/airbytehq/airbyte/pull/67933) | Update dependencies |
| 0.13.10 | 2025-10-07 | [67364](https://github.com/airbytehq/airbyte/pull/67364) | Update dependencies |
| 0.13.9 | 2025-10-06 | [67104](https://github.com/airbytehq/airbyte/pull/67104) | Increase Heartbeat Timeout to Account for cursor based streams with client side incremental and large record counts for a given day. |
| 0.13.8 | 2025-09-30 | [66789](https://github.com/airbytehq/airbyte/pull/66789) | Update dependencies |
| 0.13.7 | 2025-09-26 | [66665](https://github.com/airbytehq/airbyte/pull/66665) | Fix Typo on Error Message |
| 0.13.6 | 2025-09-09 | [66056](https://github.com/airbytehq/airbyte/pull/66056) | Update dependencies |
| 0.13.5 | 2025-08-23 | [65374](https://github.com/airbytehq/airbyte/pull/65374) | Update dependencies |
| 0.13.4 | 2025-08-09 | [63523](https://github.com/airbytehq/airbyte/pull/63523) | Update dependencies |
| 0.13.3 | 2025-07-12 | [63155](https://github.com/airbytehq/airbyte/pull/63155) | Update dependencies |
| 0.13.2 | 2025-07-05 | [62592](https://github.com/airbytehq/airbyte/pull/62592) | Update dependencies |
| 0.13.1 | 2025-06-28 | [54308](https://github.com/airbytehq/airbyte/pull/54308) | Update dependencies |
| 0.13.0 | 2025-06-25 | [62069](https://github.com/airbytehq/airbyte/pull/62069) | Promoting release candidate 0.13.0-rc.5 to a main version. |
| 0.13.0-rc.5 | 2025-06-11 | [61506](https://github.com/airbytehq/airbyte/pull/61506) | Add better error handling for companies stream, update SDM, & add advanced_auth |
| 0.13.0-rc.4 | 2025-05-15 | [60235](https://github.com/airbytehq/airbyte/pull/60235) | Add required custom paginator for 'companies' stream & Fix 500s on `Tickets` stream. |
| 0.13.0-rc.3 | 2025-05-09 | [55829](https://github.com/airbytehq/airbyte/pull/55829) | Fix pagination for `conversations`, `tickets`, `companies` & `contacts` and cleanup manifest |
| 0.13.0-rc.2 | 2025-04-08 | [57524](https://github.com/airbytehq/airbyte/pull/57524) | Use global state and pass state to parent streams for conversation_parts and company_segments |
| 0.13.0-rc.1 | 2025-02-22 | [53187](https://github.com/airbytehq/airbyte/pull/53187) | Update with latest CDK features, remove custom incremental sync components, update schema for conversation_parts |
| 0.12.2 | 2025-02-15 | [53835](https://github.com/airbytehq/airbyte/pull/53835) | Update dependencies |
| 0.12.1 | 2025-02-08 | [53257](https://github.com/airbytehq/airbyte/pull/53257) | Update dependencies |
| 0.12.0 | 2025-02-03 | [52687](https://github.com/airbytehq/airbyte/pull/52687) | New stream Tickets |
| 0.11.0 | 2025-02-03 | [51619](https://github.com/airbytehq/airbyte/pull/51619) | Upgrade API version to 2.11, add ai_agent_participated and ai_agent fields conversations stream schema |
| 0.10.1 | 2025-02-01 | [49212](https://github.com/airbytehq/airbyte/pull/49212) | Update dependencies |
| 0.10.0 | 2025-01-24 | [52132](https://github.com/airbytehq/airbyte/pull/52132) | Fix incremental sync |
| 0.9.0 | 2025-01-15 | [51570](https://github.com/airbytehq/airbyte/pull/51570) | Promoting release candidate 0.9.0-rc.2 to a main version. |
| 0.9.0-rc.2 | 2025-01-13 | [49936](https://github.com/airbytehq/airbyte/pull/49936) | Incremental substream fixes |
| 0.9.0-rc.1 | 2024-12-17 | [47240](https://github.com/airbytehq/airbyte/pull/47240) | Migrate to manifest-only format |
| 0.8.3 | 2024-12-12 | [48979](https://github.com/airbytehq/airbyte/pull/48979) | Update dependencies |
| 0.8.2 | 2024-10-29 | [47919](https://github.com/airbytehq/airbyte/pull/47919) | Update dependencies |
| 0.8.1 | 2024-10-28 | [47537](https://github.com/airbytehq/airbyte/pull/47537) | Update dependencies |
| 0.8.0 | 2024-10-23 | [46658](https://github.com/airbytehq/airbyte/pull/46658) | Add `lookback_window` to the source specification |
| 0.7.5 | 2024-10-21 | [47120](https://github.com/airbytehq/airbyte/pull/47120) | Update dependencies |
| 0.7.4 | 2024-10-12 | [46831](https://github.com/airbytehq/airbyte/pull/46831) | Update dependencies |
| 0.7.3 | 2024-10-05 | [46447](https://github.com/airbytehq/airbyte/pull/46447) | Update dependencies |
| 0.7.2 | 2024-09-28 | [45279](https://github.com/airbytehq/airbyte/pull/45279) | Update dependencies |
| 0.7.1 | 2024-08-31 | [44966](https://github.com/airbytehq/airbyte/pull/44966) | Update dependencies |
| 0.7.0 | 2024-08-29 | [44911](https://github.com/airbytehq/airbyte/pull/44911) | Migrate to CDK v4 |
| 0.6.21 | 2024-08-24 | [44672](https://github.com/airbytehq/airbyte/pull/44672) | Update dependencies |
| 0.6.20 | 2024-08-17 | [44296](https://github.com/airbytehq/airbyte/pull/44296) | Update dependencies |
| 0.6.19 | 2024-08-12 | [43878](https://github.com/airbytehq/airbyte/pull/43878) | Update dependencies |
| 0.6.18 | 2024-08-10 | [43500](https://github.com/airbytehq/airbyte/pull/43500) | Update dependencies |
| 0.6.17 | 2024-08-03 | [43276](https://github.com/airbytehq/airbyte/pull/43276) | Update dependencies |
| 0.6.16 | 2024-07-29 | [42094](https://github.com/airbytehq/airbyte/pull/42094) | Use latest CDK, raise config error on `Active subscription needed` error and transient errors for `Companies` stream. |
| 0.6.15 | 2024-07-27 | [42654](https://github.com/airbytehq/airbyte/pull/42654) | Update dependencies |
| 0.6.14 | 2024-07-20 | [42262](https://github.com/airbytehq/airbyte/pull/42262) | Update dependencies |
| 0.6.13 | 2024-07-13 | [41712](https://github.com/airbytehq/airbyte/pull/41712) | Update dependencies |
| 0.6.12 | 2024-07-10 | [41356](https://github.com/airbytehq/airbyte/pull/41356) | Update dependencies |
| 0.6.11 | 2024-07-09 | [41112](https://github.com/airbytehq/airbyte/pull/41112) | Update dependencies |
| 0.6.10 | 2024-07-06 | [40878](https://github.com/airbytehq/airbyte/pull/40878) | Update dependencies |
| 0.6.9 | 2024-06-25 | [40428](https://github.com/airbytehq/airbyte/pull/40428) | Update dependencies |
| 0.6.8 | 2024-06-22 | [39951](https://github.com/airbytehq/airbyte/pull/39951) | Update dependencies |
| 0.6.7 | 2024-06-06 | [39286](https://github.com/airbytehq/airbyte/pull/39286) | [autopull] Upgrade base image to v1.2.2 |
| 0.6.6 | 2024-05-24 | [38626](https://github.com/airbytehq/airbyte/pull/38626) | Add step granularity for activity logs stream |
| 0.6.5 | 2024-04-19 | [36644](https://github.com/airbytehq/airbyte/pull/36644) | Updating to 0.80.0 CDK |
| 0.6.4 | 2024-04-12 | [36644](https://github.com/airbytehq/airbyte/pull/36644) | Schema descriptions |
| 0.6.3 | 2024-03-23 | [36414](https://github.com/airbytehq/airbyte/pull/36414) | Fixed `pagination` regression bug for `conversations` stream |
| 0.6.2 | 2024-03-22 | [36277](https://github.com/airbytehq/airbyte/pull/36277) | Fixed the bug for `conversations` stream failed due to `404 - User Not Found`, when the `2.10` API version is used |
| 0.6.1 | 2024-03-18 | [36232](https://github.com/airbytehq/airbyte/pull/36232) | Fixed the bug caused the regression when setting the `Intercom-Version` header, updated the source to use the latest CDK version |
| 0.6.0 | 2024-02-12 | [35176](https://github.com/airbytehq/airbyte/pull/35176) | Update the connector to use `2.10` API version |
| 0.5.1 | 2024-02-12 | [35148](https://github.com/airbytehq/airbyte/pull/35148) | Manage dependencies with Poetry |
| 0.5.0 | 2024-02-09 | [35063](https://github.com/airbytehq/airbyte/pull/35063) | Add missing fields for mutiple streams |
| 0.4.0 | 2024-01-11 | [33882](https://github.com/airbytehq/airbyte/pull/33882) | Add new stream `Activity Logs` |
| 0.3.2 | 2023-12-07 | [33223](https://github.com/airbytehq/airbyte/pull/33223) | Ignore 404 error for `Conversation Parts` |
| 0.3.1 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.0 | 2023-05-25 | [29598](https://github.com/airbytehq/airbyte/pull/29598) | Update custom components to make them compatible with latest cdk version, simplify logic, update schemas |
| 0.2.1 | 2023-05-25 | [26571](https://github.com/airbytehq/airbyte/pull/26571) | Remove authSpecification from spec.json in favour of advancedAuth |
| 0.2.0 | 2023-04-05 | [23013](https://github.com/airbytehq/airbyte/pull/23013) | Migrated to Low-code (YAML Frramework) |
| 0.1.33 | 2023-03-20 | [22980](https://github.com/airbytehq/airbyte/pull/22980) | Specified date formatting in specification |
| 0.1.32 | 2023-02-27 | [22095](https://github.com/airbytehq/airbyte/pull/22095) | Extended `Contacts` schema adding `opted_out_subscription_types` property |
| 0.1.31 | 2023-02-17 | [23152](https://github.com/airbytehq/airbyte/pull/23152) | Add `TypeTransformer` to stream `companies` |
| 0.1.30 | 2023-01-27 | [22010](https://github.com/airbytehq/airbyte/pull/22010) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.29 | 2022-10-31 | [18681](https://github.com/airbytehq/airbyte/pull/18681) | Define correct version for airbyte-cdk~=0.2 |
| 0.1.28 | 2022-10-20 | [18216](https://github.com/airbytehq/airbyte/pull/18216) | Use airbyte-cdk~=0.2.0 with SQLite caching |
| 0.1.27 | 2022-08-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states |
| 0.1.26 | 2022-08-18 | [16540](https://github.com/airbytehq/airbyte/pull/16540) | Fix JSON schema |
| 0.1.25 | 2022-08-18 | [15681](https://github.com/airbytehq/airbyte/pull/15681) | Update Intercom API to v 2.5 |
| 0.1.24 | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas |
| 0.1.23 | 2022-07-19 | [14830](https://github.com/airbytehq/airbyte/pull/14830) | Added `checkpoint_interval` for Incremental streams |
| 0.1.22 | 2022-07-09 | [14554](https://github.com/airbytehq/airbyte/pull/14554) | Fixed `conversation_parts` stream schema definition |
| 0.1.21 | 2022-07-05 | [14403](https://github.com/airbytehq/airbyte/pull/14403) | Refactored  `Conversations`, `Conversation Parts`, `Company Segments` to increase performance |
| 0.1.20 | 2022-06-24 | [14099](https://github.com/airbytehq/airbyte/pull/14099) | Extended `Contacts` stream schema with `sms_consent`,`unsubscribe_from_sms` properties |
| 0.1.19 | 2022-05-25 | [13204](https://github.com/airbytehq/airbyte/pull/13204) | Fixed `conversation_parts` stream schema definition |
| 0.1.18 | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy |
| 0.1.17 | 2022-04-29 | [12374](https://github.com/airbytehq/airbyte/pull/12374) | Fixed filtering of conversation_parts |
| 0.1.16 | 2022-03-23 | [11206](https://github.com/airbytehq/airbyte/pull/11206) | Added conversation_id field to conversation_part records |
| 0.1.15 | 2022-03-22 | [11176](https://github.com/airbytehq/airbyte/pull/11176) | Correct `check_connection` URL |
| 0.1.14 | 2022-03-16 | [11208](https://github.com/airbytehq/airbyte/pull/11208) | Improve 'conversations' incremental sync speed |
| 0.1.13 | 2022-01-14 | [9513](https://github.com/airbytehq/airbyte/pull/9513) | Added handling of scroll param when it expired |
| 0.1.12 | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Updated fields and descriptions |
| 0.1.11 | 2021-12-13 | [8685](https://github.com/airbytehq/airbyte/pull/8685) | Remove time.sleep for rate limit |
| 0.1.10 | 2021-12-10 | [8637](https://github.com/airbytehq/airbyte/pull/8637) | Fix 'conversations' order and sorting. Correction of the companies stream |
| 0.1.9 | 2021-12-03 | [8395](https://github.com/airbytehq/airbyte/pull/8395) | Fix backoff of 'companies' stream |
| 0.1.8 | 2021-11-09 | [7060](https://github.com/airbytehq/airbyte/pull/7060) | Added oauth support |
| 0.1.7 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.6 | 2021-10-07 | [6879](https://github.com/airbytehq/airbyte/pull/6879) | Corrected pagination for contacts |
| 0.1.5 | 2021-09-28 | [6082](https://github.com/airbytehq/airbyte/pull/6082) | Corrected android\_last\_seen\_at field data type in schemas |
| 0.1.4 | 2021-09-20 | [6087](https://github.com/airbytehq/airbyte/pull/6087) | Corrected updated\_at field data type in schemas |
| 0.1.3 | 2021-09-08 | [5908](https://github.com/airbytehq/airbyte/pull/5908) | Corrected timestamp and arrays in schemas |
| 0.1.2 | 2021-08-19 | [5531](https://github.com/airbytehq/airbyte/pull/5531) | Corrected pagination |
| 0.1.1 | 2021-07-31 | [5123](https://github.com/airbytehq/airbyte/pull/5123) | Corrected rate limit |
| 0.1.0 | 2021-07-19 | [4676](https://github.com/airbytehq/airbyte/pull/4676) | Release Intercom CDK Connector |
</details>
