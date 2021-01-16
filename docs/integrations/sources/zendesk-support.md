# Zendesk Support

## Sync overview

The Zendesk Support source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Zendesk Support API](https://developer.zendesk.com/rest_api/docs/support).

This Source Connector is based on a [Singer Tap](https://github.com/singer-io/tap-zendesk).

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

### Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/support/usage_limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Zendesk API Token 
* Zendesk Email 
* Zendesk Subdomain 

### Setup guide

Generate a API access token using the [Zendesk support](https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

