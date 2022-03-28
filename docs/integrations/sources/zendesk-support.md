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
* [Users](https://developer.zendesk.com/rest_api/docs/support/users)

The streams below are not implemented. Please open a Github issue or request it through Airbyte Cloud's support box if you are interested in them.

**Tickets**

* [Ticket Attachments](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket-attachments/)
* [Ticket Requests](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket-requests/)
* [Ticket Activities](https://developer.zendesk.com/api-reference/ticketing/tickets/activity_stream/)
* [Ticket Skips](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/)

**Help Center**

* [Articles](https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/)
* [Article Attachments](https://developer.zendesk.com/api-reference/help_center/help-center-api/article_attachments/)
* [Article Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/article_comments/)
* [Categories](https://developer.zendesk.com/api-reference/help_center/help-center-api/categories/)
* [Management Permission Groups](https://developer.zendesk.com/api-reference/help_center/help-center-api/permission_groups/)
* [Translations](https://developer.zendesk.com/api-reference/help_center/help-center-api/translations/)
* [Sections](https://developer.zendesk.com/api-reference/help_center/help-center-api/sections/)
* [Topics](https://developer.zendesk.com/api-reference/help_center/help-center-api/topics)
* [Themes](https://developer.zendesk.com/api-reference/help_center/help-center-api/theming)
* [Posts](https://developer.zendesk.com/api-reference/help_center/help-center-api/posts)
* [Themes](https://developer.zendesk.com/api-reference/help_center/help-center-api/posts)
* [Post Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/post_comments/)

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

### Requirements

* Zendesk Subdomain
* Auth Method
  * API Token
    * Zendesk API Token 
    * Zendesk Email 
  * OAuth2.0 (obtain access_token by authorising your Zendesk Account)

### Setup guide

* API Token
Generate a API access token using the [Zendesk support](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

* OAuth2.0 (Only for Airbyte Cloud)
Simply proceed by pressing "Authenticate your Account" and complete the authentication with your Zendesk credentials.

### CHANGELOG

| Version  | Date       | Pull Request | Subject                                                |
|:---------|:-----------| :-----       |:-------------------------------------------------------|
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
