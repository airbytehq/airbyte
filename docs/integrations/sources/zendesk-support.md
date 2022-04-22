# Zendesk Support

## Sync overview

The Zendesk Support source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Zendesk Support API](https://developer.zendesk.com/api-reference/apps/apps-support-api/introduction/). This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python). Incremental sync are implemented on API side by its filters

### Output schema

This Source is capable of syncing the following core Streams:

* [Brands](https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands)
* [Custom Roles](https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles)
* [Groups](https://developer.zendesk.com/rest_api/docs/support/groups)
* [Group Memberships](https://developer.zendesk.com/rest_api/docs/support/group_memberships)
* [Macros](https://developer.zendesk.com/rest_api/docs/support/macros)
* [Organizations](https://developer.zendesk.com/rest_api/docs/support/organizations)
* [Satisfaction Ratings](https://developer.zendesk.com/rest_api/docs/support/satisfaction_ratings)
* [Schedules](https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules)
* [SLA Policies](https://developer.zendesk.com/rest_api/docs/support/sla_policies)
* [Tags](https://developer.zendesk.com/rest_api/docs/support/tags)
* [Tickets](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based)
* [Ticket Audits](https://developer.zendesk.com/rest_api/docs/support/ticket_audits)
* [Ticket Comments](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export)
* [Ticket Fields](https://developer.zendesk.com/rest_api/docs/support/ticket_fields)
* [Ticket Forms](https://developer.zendesk.com/rest_api/docs/support/ticket_forms)
* [Ticket Metrics](https://developer.zendesk.com/rest_api/docs/support/ticket_metrics)
* [Ticket Metric Events](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/)
* [Users](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export)

### Data type mapping

| Integration Type | Airbyte Type |
| :--- | :--- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Debuped + History Sync | Yes | Enabled according to type of destination |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/support/usage_limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started
1. Click `Authenticate your Zendesk account`
2. Enter a `Start Date` as the minimum date of your data replication.
3. Enter your `Subdomain`. Learn how to find it in the `Requirements` section.
4. Click on `Setup Source`.
5. You're now ready to sync your data.

### Requirements

* `Subdomain` - this is your Zendesk subdomain that can be found in your account URL. For example, in `https://{MY_SUBDOMAIN}.zendesk.com/`, where `MY_SUBDOMAIN` is the value of your subdomain.
* `Authentication` - Zendesk service provides two authentication methods. Choose between: `OAuth2.0` or `API token`.
  * Authentication using `OAuth2.0` (Only for Airbyte Cloud) - obtain `access_token` by authorising using your Zendesk Account credentials. Simply proceed by pressing "Authenticate your Zendesk Account" and complete the authentication.
  * Authentication using `API Token`:
    * `API Token` - the value of the API token generated. See the [generating API Token](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token) for more information.
    * `Email` - the user email for your Zendesk account.


### CHANGELOG

| Version  | Date       | Pull Request | Subject                                                |
|:---------|:-----------| :-----       |:-------------------------------------------------------|
| `0.2.6`  | 2022-04-19 | [12122](https://github.com/airbytehq/airbyte/pull/12122) | Fixed the bug when only 100,000 Users are synced [11895](https://github.com/airbytehq/airbyte/issues/11895) and fixed bug when `start_date` is not used on user stream [12059](https://github.com/airbytehq/airbyte/issues/12059).
| `0.2.5`  | 2022-04-05 | [11727](https://github.com/airbytehq/airbyte/pull/11727) | Fixed the bug when state was not parsed correctly
| `0.2.4`  | 2022-04-04 | [11688](https://github.com/airbytehq/airbyte/pull/11688) | Small documentation corrections
| `0.2.3`  | 2022-03-23 | [11349](https://github.com/airbytehq/airbyte/pull/11349) | Fixed the bug when Tickets stream didn't return deleted records
| `0.2.2`  | 2022-03-17 | [11237](https://github.com/airbytehq/airbyte/pull/11237) | Fixed the bug when TicketComments stream didn't return all records
| `0.2.1`  | 2022-03-15 | [11162](https://github.com/airbytehq/airbyte/pull/11162) | Added support of OAuth2.0 authentication method
| `0.2.0`  | 2022-03-01 | [9456](https://github.com/airbytehq/airbyte/pull/9456) | Update source to use future requests                   |
| `0.1.12` | 2022-01-25 | [9785](https://github.com/airbytehq/airbyte/pull/9785) | Add additional log messages                            |
| `0.1.11` | 2021-12-21 | [8987](https://github.com/airbytehq/airbyte/pull/8987) | Update connector fields title/description              |
| `0.1.9`  | 2021-12-16 | [8616](https://github.com/airbytehq/airbyte/pull/8616) | Adds Brands, CustomRoles and Schedules streams         |
| `0.1.8`  | 2021-11-23 | [8050](https://github.com/airbytehq/airbyte/pull/8168) | Adds TicketMetricEvents stream                         |
| `0.1.7`  | 2021-11-23 | [8058](https://github.com/airbytehq/airbyte/pull/8058) | Added support of AccessToken authentication            |
| `0.1.6`  | 2021-11-18 | [8050](https://github.com/airbytehq/airbyte/pull/8050) | Fix wrong types for schemas, add TypeTransformer       |
| `0.1.5`  | 2021-10-26 | [7679](https://github.com/airbytehq/airbyte/pull/7679) | Add ticket_id and ticket_comments                      |
| `0.1.4`  | 2021-10-26 | [7377](https://github.com/airbytehq/airbyte/pull/7377) | Fix initially_assigned_at type in ticket metrics       |
| `0.1.3`  | 2021-10-17 | [7097](https://github.com/airbytehq/airbyte/pull/7097) | Corrected the connector's specification                |
| `0.1.2`  | 2021-10-16 | [6513](https://github.com/airbytehq/airbyte/pull/6513) | Fixed TicketComments stream                            |
| `0.1.1`  | 2021-09-02 | [5787](https://github.com/airbytehq/airbyte/pull/5787) | Fixed incremental logic for the ticket_comments stream |
| `0.1.0`  | 2021-07-21 | [4861](https://github.com/airbytehq/airbyte/pull/4861) | Created CDK native zendesk connector                   |
