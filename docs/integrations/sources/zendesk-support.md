# Zendesk Support

This page guides you through setting up the Zendesk Support source connector.

## Prerequisites

- Locate your Zendesk subdomain found in your account URL. For example, if your account URL is `https://{MY_SUBDOMAIN}.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.
- (For Airbyte Open Source) Find the email address associated with your Zendesk account. Also, generate an [API token](https://support.zendesk.com/hc/en-us/articles/4408889192858-Generating-a-new-API-token) for the account.

## Set up the Zendesk Support source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Zendesk Support** from the Source type dropdown.
4. Enter a name for your source.
5. For **Subdomain**, enter your [Zendesk subdomain](#prerequisites).
6. For **Start date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. You can use OAuth or an API key to authenticate your Zendesk Support account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.
    - To authenticate using OAuth for Airbyte Cloud, click **Authenticate your Zendesk Support account** to sign in with Zendesk Support and authorize your account. 
    - To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter your [API key](#prerequisites). Enter the **Email** associated with your Zendesk Support account.   
8. Click **Set up source**.

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

* [Brands](https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands)
* [Custom Roles](https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles)
* [Groups](https://developer.zendesk.com/rest_api/docs/support/groups) \(Incremental\)
* [Group Memberships](https://developer.zendesk.com/rest_api/docs/support/group_memberships) \(Incremental\)
* [Macros](https://developer.zendesk.com/rest_api/docs/support/macros) \(Incremental\)
* [Organizations](https://developer.zendesk.com/rest_api/docs/support/organizations) \(Incremental\)
* [Satisfaction Ratings](https://developer.zendesk.com/rest_api/docs/support/satisfaction_ratings) \(Incremental\)
* [Schedules](https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules)
* [SLA Policies](https://developer.zendesk.com/rest_api/docs/support/sla_policies)
* [Tags](https://developer.zendesk.com/rest_api/docs/support/tags)
* [Tickets](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based) \(Incremental\)
* [Ticket Audits](https://developer.zendesk.com/rest_api/docs/support/ticket_audits) \(Client-Side Incremental\)
* [Ticket Comments](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export)  \(Incremental\)
* [Ticket Fields](https://developer.zendesk.com/rest_api/docs/support/ticket_fields) \(Incremental\)
* [Ticket Forms](https://developer.zendesk.com/rest_api/docs/support/ticket_forms) \(Incremental\)
* [Ticket Metrics](https://developer.zendesk.com/rest_api/docs/support/ticket_metrics) \(Incremental\)
* [Ticket Metric Events](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/) \(Incremental\)
* [Users](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export) \(Incremental\)

## Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/support/usage_limits).

The Zendesk connector ideally should not run into Zendesk API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                            |
|:---------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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
