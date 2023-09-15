# Zendesk Support

This page contains the setup guide and reference information for the Zendesk Support source connector.

## Prerequisites

- A Zendesk account with an Administrator role.

## Setup guide

The Zendesk Support source connector supports two authentication methods:

- OAuth 2.0
- API token

<!-- env:cloud -->
For **Airbyte Cloud** users, we highly recommend using OAuth to authenticate your Zendesk Support account, as it simplifies the setup process and allows you to authenticate [directly from the Airbyte UI](#set-up-the-zendesk-support-source-connector).
<!-- /env:cloud -->
<!-- env:oss -->
For **Airbyte Open Source** users, we recommend using an API token to authenticate your Zendesk Support account. Please follow the steps below to generate this key.

:::note
If you prefer to authenticate with OAuth for **Airbyte Open Source**, you can follow the steps laid out in [this Zendesk article](https://support.zendesk.com/hc/en-us/articles/4408845965210) to obtain your client ID, client secret and access token. Please ensure you set the scope to `read` when generating the access token.
:::

### (Airbyte Open Source) Enable API token access and generate a token

1. Log in to your Zendesk account.
2. Click the **Zendesk Products** icon (four squares) in the top-right corner, then select **Admin Center**.
3. In the left navbar, click **Apps and Integrations**, then select **APIs** > **Zendesk API**.
4. In the **Settings** tab, toggle the option to enable token access.
5. Click the **Add API token** button. You may optionally provide a token description.

   :::caution
   Be sure to copy the token and save it in a secure location. You will not be able to access the token's value after you close the page.
   :::

6. Click **Save**.
<!-- /env:oss -->

### Set up the Zendesk Support source connector

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Zendesk Support** from the list of available sources.
4. For **Source name**, enter a name to help you identify this source.
5. You can use OAuth or an API token to authenticate your Zendesk Support account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.

   <!-- env:cloud -->
   - **For Airbyte Cloud**: To authenticate using OAuth, select **OAuth 2.0** from the Authentication dropdown, then click **Authenticate your Zendesk Support account** to sign in with Zendesk Support and authorize your account.
   <!-- /env:cloud -->
   <!-- env:oss -->
   - **For Airbyte Open Source**: To authenticate using an API key, select **API Token** from the Authentication dropdown and enter the API token you generated, as well as the email address associated with your Zendesk Support account.
   <!-- /env:oss -->

6. For **Subdomain**, enter your Zendesk subdomain. This is the subdomain found in your account URL. For example, if your account URL is `https://MY_SUBDOMAIN.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.
7. (Optional) For **Start Date**, use the provided datepicker or enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated. If this field is left blank, Airbyte will replicate the data for the last two years by default.
8. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Zendesk Support source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental Sync | Append
- Incremental Sync | Deduped History

## Supported streams

:::note
There are two types of incremental sync:

1. Incremental (standard server-side, where API returns only the data updated or generated since the last sync)
2. Client-Side Incremental (API returns all available data and connector filters out only new records)
:::

The Zendesk Support source connector supports the following streams:

- [Account Attributes](https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-account-attributes)
- [Articles](https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/#list-articles) \(Incremental\) 
- [Article Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) \(Incremental\) 
- [Article Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/article_comments/#list-comments) \(Incremental\) 
- [Article Comment Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) \(Incremental\) 
- [Attribute Definitions](https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-routing-attribute-definitions)
- [Audit Logs](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs)\(Incremental\) (Only available for enterprise accounts)
- [Brands](https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands)
- [Custom Roles](https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles) \(Incremental\)
- [Deleted Tickets](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#list-deleted-tickets) \(Incremental\)
- [Groups](https://developer.zendesk.com/rest_api/docs/support/groups) \(Incremental\)
- [Group Memberships](https://developer.zendesk.com/rest_api/docs/support/group_memberships) \(Incremental\)
- [Macros](https://developer.zendesk.com/rest_api/docs/support/macros) \(Incremental\)
- [Organizations](https://developer.zendesk.com/rest_api/docs/support/organizations) \(Incremental\)
- [Organization Fields](https://developer.zendesk.com/api-reference/ticketing/organizations/organization_fields/#list-organization-fields) \(Incremental\)
- [Organization Memberships](https://developer.zendesk.com/api-reference/ticketing/organizations/organization_memberships/) \(Incremental\)
- [Posts](https://developer.zendesk.com/api-reference/help_center/help-center-api/posts/#list-posts) \(Incremental\)
- [Post Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/post_comments/#list-comments) \(Incremental\)
- [Post Comment Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) \(Incremental\)
- [Post Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) \(Incremental\)
- [Satisfaction Ratings](https://developer.zendesk.com/rest_api/docs/support/satisfaction_ratings) \(Incremental\)
- [Schedules](https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules) \(Incremental\)
- [SLA Policies](https://developer.zendesk.com/rest_api/docs/support/sla_policies) \(Incremental\)
- [Tags](https://developer.zendesk.com/rest_api/docs/support/tags)
- [Tickets](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based) \(Incremental\)
- [Ticket Audits](https://developer.zendesk.com/rest_api/docs/support/ticket_audits) \(Client-Side Incremental\)
- [Ticket Comments](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export) \(Incremental\)
- [Ticket Fields](https://developer.zendesk.com/rest_api/docs/support/ticket_fields) \(Incremental\)
- [Ticket Forms](https://developer.zendesk.com/rest_api/docs/support/ticket_forms) \(Incremental\)
- [Ticket Metrics](https://developer.zendesk.com/rest_api/docs/support/ticket_metrics) \(Incremental\)
- [Ticket Metric Events](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/) \(Incremental\)
- [Topics](https://developer.zendesk.com/api-reference/help_center/help-center-api/topics/#list-topics) \(Incremental\)
- [Ticket Skips](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/) \(Incremental\)
- [Users](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export) \(Incremental\)
- [UserFields](https://developer.zendesk.com/api-reference/ticketing/users/user_fields/#list-user-fields)

## Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/support/usage_limits).

The Zendesk connector ideally should not run into Zendesk API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                            |
|:---------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `1.7.0`  | 2023-09-11 | [30259](https://github.com/airbytehq/airbyte/pull/30259) | Add stream `Deleted Tickets`                                                                                                                                                                                                       |
| `1.6.0`  | 2023-09-09 | [30168](https://github.com/airbytehq/airbyte/pull/30168) | Make `start_date` field optional                                                                                                                                                                                                   |
| `1.5.1`  | 2023-09-05 | [30142](https://github.com/airbytehq/airbyte/pull/30142) | Handle non-JSON Response                                                                                                                                                                                                           |
| `1.5.0`  | 2023-09-04 | [30138](https://github.com/airbytehq/airbyte/pull/30138) | Add new Streams: `Article Votes`, `Article Comments`, `Article Comment Votes`                                                                                                                                                      |
| `1.4.0`  | 2023-09-04 | [30134](https://github.com/airbytehq/airbyte/pull/30134) | Add incremental support for streams: `custom Roles`, `Schedules`, `SLA Policies`                                                                                                                                                   |
| `1.3.0`  | 2023-08-30 | [30031](https://github.com/airbytehq/airbyte/pull/30031) | Add new streams: `Articles`, `Organization Fields`                                                                                                                                                                                 |
| `1.2.2`  | 2023-08-30 | [29998](https://github.com/airbytehq/airbyte/pull/29998) | Fix typo in stream `AttributeDefinitions`: field condition                                                                                                                                                                         |
| `1.2.1`  | 2023-08-30 | [29991](https://github.com/airbytehq/airbyte/pull/29991) | Remove Custom availability strategy                                                                                                                                                                                                |
| `1.2.0`  | 2023-08-29 | [29940](https://github.com/airbytehq/airbyte/pull/29940) | Add undeclared fields to schemas                                                                                                                                                                                                   |
| `1.1.1`  | 2023-08-29 | [29904](https://github.com/airbytehq/airbyte/pull/29904) | make `Organizations` stream incremental                                                                                                                                                                                            |
| `1.1.0`  | 2023-08-28 | [29891](https://github.com/airbytehq/airbyte/pull/29891) | Add stream `UserFields`                                                                                                                                                                                                            |
| `1.0.0`  | 2023-07-27 | [28774](https://github.com/airbytehq/airbyte/pull/28774) | fix retry logic & update cursor for `Tickets` stream                                                                                                                                                                               |
| `0.11.0` | 2023-08-10 | [27208](https://github.com/airbytehq/airbyte/pull/27208) | Add stream `Topics`                                                                                                                                                                                                                |
| `0.10.7` | 2023-08-09 | [29256](https://github.com/airbytehq/airbyte/pull/29256) | Update tooltip descriptions in spec                                                                                                                                                                                                |
| `0.10.6` | 2023-08-04 | [29031](https://github.com/airbytehq/airbyte/pull/29031) | Reverted `advancedAuth` spec changes                                                                                                                                                                                               |
| `0.10.5` | 2023-08-01 | [28910](https://github.com/airbytehq/airbyte/pull/28910) | Updated `advancedAuth` broken references                                                                                                                                                                                           |
| `0.10.4` | 2023-07-25 | [28397](https://github.com/airbytehq/airbyte/pull/28397) | Handle 404 Error                                                                                                                                                                                                                   |
| `0.10.3` | 2023-07-24 | [28612](https://github.com/airbytehq/airbyte/pull/28612) | Fix pagination for stream `TicketMetricEvents`                                                                                                                                                                                     |
| `0.10.2` | 2023-07-19 | [28487](https://github.com/airbytehq/airbyte/pull/28487) | Remove extra page from params                                                                                                                                                                                                      |
| `0.10.1` | 2023-07-10 | [28096](https://github.com/airbytehq/airbyte/pull/28096) | Replace `offset` pagination with `cursor` pagination                                                                                                                                                                               |
| `0.10.0` | 2023-07-06 | [27991](https://github.com/airbytehq/airbyte/pull/27991) | Add streams: `PostVotes`, `PostCommentVotes`                                                                                                                                                                                       |
| `0.9.0`  | 2023-07-05 | [27961](https://github.com/airbytehq/airbyte/pull/27961) | Add stream: `Post Comments`                                                                                                                                                                                                        |
| `0.8.1`  | 2023-06-27 | [27765](https://github.com/airbytehq/airbyte/pull/27765) | Bugfix: Nonetype error while syncing more then 100000 organizations                                                                                                                                                                |
| `0.8.0`  | 2023-06-09 | [27156](https://github.com/airbytehq/airbyte/pull/27156) | Add stream `Posts`                                                                                                                                                                                                                 |
| `0.7.0`  | 2023-06-27 | [27436](https://github.com/airbytehq/airbyte/pull/27436) | Add Ticket Skips stream                                                                                                                                                                                                            |
| `0.6.0`  | 2023-06-27 | [27450](https://github.com/airbytehq/airbyte/pull/27450) | Add Skill Based Routing streams                                                                                                                                                                                                    |
| `0.5.0`  | 2023-06-26 | [27735](https://github.com/airbytehq/airbyte/pull/27735) | License Update: Elv2 stream stream                                                                                                                                                                                                 |
| `0.4.0`  | 2023-06-16 | [27431](https://github.com/airbytehq/airbyte/pull/27431) | Add Organization Memberships stream                                                                                                                                                                                                |
| `0.3.1`  | 2023-06-02 | [26945](https://github.com/airbytehq/airbyte/pull/26945) | Make `Ticket Metrics` stream to use cursor pagination                                                                                                                                                                              |
| `0.3.0`  | 2023-05-23 | [26347](https://github.com/airbytehq/airbyte/pull/26347) | Add stream `Audit Logs` logs`                                                                                                                                                                                                      |
| `0.2.30` | 2023-05-23 | [26414](https://github.com/airbytehq/airbyte/pull/26414) | Added missing handlers when `empty json` or `JSONDecodeError` is received                                                                                                                                                          |
| `0.2.29` | 2023-04-18 | [25214](https://github.com/airbytehq/airbyte/pull/25214) | Add missing fields to `Tickets` stream                                                                                                                                                                                             |
| `0.2.28` | 2023-03-21 | [24053](https://github.com/airbytehq/airbyte/pull/24053) | Fix stream `sla_policies` schema data type error (events.value)                                                                                                                                                                    |
| `0.2.27` | 2023-03-22 | [22817](https://github.com/airbytehq/airbyte/pull/22817) | Specified date formatting in specification                                                                                                                                                                                         |
| `0.2.26` | 2023-03-20 | [24252](https://github.com/airbytehq/airbyte/pull/24252) | Handle invalid `start_date` when checking connection                                                                                                                                                                               |
| `0.2.25` | 2023-02-28 | [22308](https://github.com/airbytehq/airbyte/pull/22308) | Add `AvailabilityStrategy` for all streams                                                                                                                                                                                         |
| `0.2.24` | 2023-02-17 | [23246](https://github.com/airbytehq/airbyte/pull/23246) | Handle `StartTimeTooRecent` error for Tickets stream                                                                                                                                                                               |
| `0.2.23` | 2023-02-15 | [23035](https://github.com/airbytehq/airbyte/pull/23035) | Handle 403 Error                                                                                                                                                                                                                   |
| `0.2.22` | 2023-02-14 | [22483](https://github.com/airbytehq/airbyte/pull/22483) | Fix test; handle 400 error                                                                                                                                                                                                         |
| `0.2.21` | 2023-01-27 | [22027](https://github.com/airbytehq/airbyte/pull/22027) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                                                                        |
| `0.2.20` | 2022-12-28 | [20900](https://github.com/airbytehq/airbyte/pull/20900) | Remove synchronous time.sleep, add logging, reduce backoff time                                                                                                                                                                    |
| `0.2.19` | 2022-12-09 | [19967](https://github.com/airbytehq/airbyte/pull/19967) | Fix reading response for more than 100k records                                                                                                                                                                                    |
| `0.2.18` | 2022-11-29 | [19432](https://github.com/airbytehq/airbyte/pull/19432) | Revert changes from version 0.2.15, use a test read instead                                                                                                                                                                        |
| `0.2.17` | 2022-11-24 | [19792](https://github.com/airbytehq/airbyte/pull/19792) | Transform `ticket_comments.via` "-" to null                                                                                                                                                                                        |
| `0.2.16` | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                                                                                                                                                      |
| `0.2.15` | 2022-08-03 | [15233](https://github.com/airbytehq/airbyte/pull/15233) | Added `subscription plan` check on `streams discovery` step to remove streams that are not accessible for fetch due to subscription plan restrictions                                                                              |
| `0.2.14` | 2022-07-27 | [15036](https://github.com/airbytehq/airbyte/pull/15036) | Convert `ticket_audits.previous_value` values to string                                                                                                                                                                            |
| `0.2.13` | 2022-07-21 | [14829](https://github.com/airbytehq/airbyte/pull/14829) | Convert `tickets.custom_fields` values to string                                                                                                                                                                                   |
| `0.2.12` | 2022-06-30 | [14304](https://github.com/airbytehq/airbyte/pull/14304) | Fixed Pagination for Group Membership stream                                                                                                                                                                                       |
| `0.2.11` | 2022-06-24 | [14112](https://github.com/airbytehq/airbyte/pull/14112) | Fixed "Retry-After" non integer value                                                                                                                                                                                              |
| `0.2.10` | 2022-06-14 | [13757](https://github.com/airbytehq/airbyte/pull/13757) | Fixed the bug with `TicketMetrics` stream, HTTP Error 429, caused by lots of API requests                                                                                                                                          |
| `0.2.9`  | 2022-05-27 | [13261](https://github.com/airbytehq/airbyte/pull/13261) | Bugfix for the unhandled [ChunkedEncodingError](https://github.com/airbytehq/airbyte/issues/12591) and [ConnectionError](https://github.com/airbytehq/airbyte/issues/12155)                                                        |
| `0.2.8`  | 2022-05-20 | [13055](https://github.com/airbytehq/airbyte/pull/13055) | Fixed minor issue for stream `ticket_audits` schema                                                                                                                                                                                |
| `0.2.7`  | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Adding fixtures to mock time.sleep for connectors that explicitly sleep                                                                                                                                                            |
| `0.2.6`  | 2022-04-19 | [12122](https://github.com/airbytehq/airbyte/pull/12122) | Fixed the bug when only 100,000 Users are synced [11895](https://github.com/airbytehq/airbyte/issues/11895) and fixed bug when `start_date` is not used on user stream [12059](https://github.com/airbytehq/airbyte/issues/12059). |
| `0.2.5`  | 2022-04-05 | [11727](https://github.com/airbytehq/airbyte/pull/11727) | Fixed the bug when state was not parsed correctly                                                                                                                                                                                  |
| `0.2.4`  | 2022-04-04 | [11688](https://github.com/airbytehq/airbyte/pull/11688) | Small documentation corrections                                                                                                                                                                                                    |
| `0.2.3`  | 2022-03-23 | [11349](https://github.com/airbytehq/airbyte/pull/11349) | Fixed the bug when Tickets stream didn't return deleted records                                                                                                                                                                    |
| `0.2.2`  | 2022-03-17 | [11237](https://github.com/airbytehq/airbyte/pull/11237) | Fixed the bug when TicketComments stream didn't return all records                                                                                                                                                                 |
| `0.2.1`  | 2022-03-15 | [11162](https://github.com/airbytehq/airbyte/pull/11162) | Added support of OAuth2.0 authentication method                                                                                                                                                                                    |
| `0.2.0`  | 2022-03-01 | [9456](https://github.com/airbytehq/airbyte/pull/9456)   | Update source to use future requests                                                                                                                                                                                               |
| `0.1.12` | 2022-01-25 | [9785](https://github.com/airbytehq/airbyte/pull/9785)   | Add additional log messages                                                                                                                                                                                                        |
| `0.1.11` | 2021-12-21 | [8987](https://github.com/airbytehq/airbyte/pull/8987)   | Update connector fields title/description                                                                                                                                                                                          |
| `0.1.9`  | 2021-12-16 | [8616](https://github.com/airbytehq/airbyte/pull/8616)   | Adds Brands, CustomRoles and Schedules streams                                                                                                                                                                                     |
| `0.1.8`  | 2021-11-23 | [8050](https://github.com/airbytehq/airbyte/pull/8168)   | Adds TicketMetricEvents stream                                                                                                                                                                                                     |
| `0.1.7`  | 2021-11-23 | [8058](https://github.com/airbytehq/airbyte/pull/8058)   | Added support of AccessToken authentication                                                                                                                                                                                        |
| `0.1.6`  | 2021-11-18 | [8050](https://github.com/airbytehq/airbyte/pull/8050)   | Fix wrong types for schemas, add TypeTransformer                                                                                                                                                                                   |
| `0.1.5`  | 2021-10-26 | [7679](https://github.com/airbytehq/airbyte/pull/7679)   | Add ticket_id and ticket_comments                                                                                                                                                                                                  |
| `0.1.4`  | 2021-10-26 | [7377](https://github.com/airbytehq/airbyte/pull/7377)   | Fix initially_assigned_at type in ticket metrics                                                                                                                                                                                   |
| `0.1.3`  | 2021-10-17 | [7097](https://github.com/airbytehq/airbyte/pull/7097)   | Corrected the connector's specification                                                                                                                                                                                            |
| `0.1.2`  | 2021-10-16 | [6513](https://github.com/airbytehq/airbyte/pull/6513)   | Fixed TicketComments stream                                                                                                                                                                                                        |
| `0.1.1`  | 2021-09-02 | [5787](https://github.com/airbytehq/airbyte/pull/5787)   | Fixed incremental logic for the ticket_comments stream                                                                                                                                                                             |
| `0.1.0`  | 2021-07-21 | [4861](https://github.com/airbytehq/airbyte/pull/4861)   | Created CDK native zendesk connector                                                                                                                                                                                               |
