# Zendesk Support

## Sync overview

The Zendesk Support source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Zendesk Support API](https://developer.zendesk.com/api-reference/apps/apps-support-api/introduction/).
This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).
Incremental sync are implemented on API side by its filters
### Output schema

This Source is capable of syncing the following core Streams:

* [Tickets](https://developer.zendesk.com/rest_api/docs/support/tickets)
* [Groups](https://developer.zendesk.com/rest_api/docs/support/groups)
* [Users](https://developer.zendesk.com/rest_api/docs/support/users)
* [Organizations](https://developer.zendesk.com/rest_api/docs/support/organizations)
* [Ticket Audits](https://developer.zendesk.com/rest_api/docs/support/ticket_audits)
* [Ticket Comments](https://developer.zendesk.com/rest_api/docs/support/ticket_comments)
* [Ticket Fields](https://developer.zendesk.com/rest_api/docs/support/ticket_fields)
* [Ticket Forms](https://developer.zendesk.com/rest_api/docs/support/ticket_forms)
* [Ticket Metrics](https://developer.zendesk.com/rest_api/docs/support/ticket_metrics)
* [Group Memberships](https://developer.zendesk.com/rest_api/docs/support/group_memberships)
* [Macros](https://developer.zendesk.com/rest_api/docs/support/macros)
* [Satisfaction Ratings](https://developer.zendesk.com/rest_api/docs/support/satisfaction_ratings)
* [Tags](https://developer.zendesk.com/rest_api/docs/support/tags)
* [SLA Policies](https://developer.zendesk.com/rest_api/docs/support/sla_policies)

 ### Not implemented schema
 These Zendesk endpoints are available too. But syncing with them will be implemented in the future.
 #### Tickets
* [Ticket Attachments](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket-attachments/)
* [Ticket Requests](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket-requests/)
* [Ticket Metric Events](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/)
* [Ticket Activities](https://developer.zendesk.com/api-reference/ticketing/tickets/activity_stream/)
* [Ticket Skips](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/)

 #### Help Center
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

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |
### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Debuped + History Sync | Yes | Enabled according to type of destination  |
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
  * oAuth2 (not implemented)


### Setup guide

Generate a API access token using the [Zendesk support](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

### CHANGELOG
| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.1` | 2021-09-02 | [5787](https://github.com/airbytehq/airbyte/pull/5787) | fixed incremental logic for the ticket_comments stream |
| `0.1.0` | 2021-07-21 | [4861](https://github.com/airbytehq/airbyte/pull/4861) | created CDK native zendesk connector |

