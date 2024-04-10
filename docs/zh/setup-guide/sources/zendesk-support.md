# Zendesk Support

This page contains the setup guide and reference information for Zendesk Support.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes |
| Incremental - Deduped | Yes |

There are two types of incremental sync:

* Incremental (standard server-side, where API returns only the data updated or generated since the last sync).
* Client-Side Incremental (API returns all available data and integration filters out only new records).

## Prerequisites

* A Zendesk account with an Administrator role
* Zendesk API token
* Zendesk subdomain

## Setup guide

### Step 1: Generate an API token

1. Inside your Zendesk account, click the Zendesk Products icon (four squares) in the top-right corner, then select **Admin Center**.
![Zendesk Admin Center](/docs/setup-guide/assets/images/zendesk-admin-center.jpg "Zendesk Admin Center")

2. In the left navbar, scroll down to **Apps and Integrations**, then select **APIs** > **Zendesk API**.
![Zendesk API](/docs/setup-guide/assets/images/zendesk-api.jpg "Zendesk API")

3. In the **Settings** tab, toggle the option to enable token access.
![Zendesk Enable Token Access](/docs/setup-guide/assets/images/zendesk-enable-token-access.jpg "Zendesk Enable Token Access")

4. Click the **Add API token** button. And then click Save.
![Zendesk API Token](/docs/setup-guide/assets/images/zendesk-api-token.jpg "Zendesk API Token")

  > CAUTION: Be sure to copy the token and save it in a secure location. You will not be able to access the token's value after you close the page.

### Step 2: Set up Zendesk Support in Daspire

1. Select **Zendesk Support** from the Source list.

2. Enter a **Source Name**.

3. To authenticate your account, select **API Token** and enter the API token you generated in Step 1, as well as the email address associated with your Zendesk Support account.

4. For **Subdomain**, enter your Zendesk subdomain. This is the subdomain found in your account URL. For example, if your account URL is `https://MY_SUBDOMAIN.zendesk.com/`, then `MY_SUBDOMAIN` is your subdomain.

5. (Optional) For **Start Date**, enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated. If this field is left blank, Daspire will replicate the data for the last two years by default.

6. Click **Save & Test**.

## Output schema

This Source is capable of syncing the following core Streams:

* [Account Attributes](https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-account-attributes)
* [Articles](https://developers.notion.com/reference/retrieve-a-comment) (Incremental)
* [Article Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) (Incremental)
* [Article Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/article_comments/#list-comments) (Incremental)
* [Article Comment Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) (Incremental)
* [Attribute Definitions](https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-routing-attribute-definitions)
* [Audit Logs](https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs) (Incremental, only available for enterprise accounts)
* [Brands](https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands)
* [Custom Roles](https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles) (Incremental)
* [Groups](https://developer.zendesk.com/rest_api/docs/support/groups) (Incremental)
* [Group Memberships](https://developer.zendesk.com/rest_api/docs/support/group_memberships) (Incremental)
* [Macros](https://developer.zendesk.com/rest_api/docs/support/macros) (Incremental)
* [Organizations](https://developer.zendesk.com/rest_api/docs/support/organizations) (Incremental)
* [Organization Fields](https://developer.zendesk.com/api-reference/ticketing/organizations/organization_fields/#list-organization-fields) (Incremental)
* [Organization Memberships](https://developer.zendesk.com/api-reference/ticketing/organizations/organization_memberships/) (Incremental)
* [Posts](https://developer.zendesk.com/api-reference/help_center/help-center-api/posts/#list-posts) (Incremental)
* [Post Comments](https://developer.zendesk.com/api-reference/help_center/help-center-api/post_comments/#list-comments) (Incremental)
* [Post Comment Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) (Incremental)
* [Post Votes](https://developer.zendesk.com/api-reference/help_center/help-center-api/votes/#list-votes) (Incremental)
* [Satisfaction Ratings](https://developer.zendesk.com/rest_api/docs/support/satisfaction_ratings) (Incremental)
* [Schedules](https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules) (Incremental)
* [SLA Policies](https://developer.zendesk.com/rest_api/docs/support/sla_policies) (Incremental)
* [Tags](https://developer.zendesk.com/rest_api/docs/support/tags)
* [Tickets](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based) (Incremental)
* [Ticket Audits](https://developer.zendesk.com/rest_api/docs/support/ticket_audits) (Client-side incremental)
* [Ticket Comments](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export) (Incremental)
* [Ticket Fields](https://developer.zendesk.com/rest_api/docs/support/ticket_fields) (Incremental)
* [Ticket Forms](https://developer.zendesk.com/rest_api/docs/support/ticket_forms) (Incremental)
* [Ticket Metrics](https://developer.zendesk.com/rest_api/docs/support/ticket_metrics) (Incremental)
* [Ticket Metric Events](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/) (Incremental)
* [Topics](https://developer.zendesk.com/api-reference/help_center/help-center-api/topics/#list-topics) (Incremental)
* [Ticket Skips](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/) (Incremental)
* [Users](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export) (Incremental)
* [UserFields](https://developer.zendesk.com/api-reference/ticketing/users/user_fields/#list-user-fields)

### Deleted records support

The Zendesk Support integration fetches deleted records in the following streams:

| Stream | Deletion indicator field |
| --- | --- |
| Brands | `is_deleted` |
| Groups | `deleted` |
| Organizations	 | `deleted_at` |
| Ticket Metric Events | `deleted` |
| Tickets | `status==deleted` |

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

The integration is restricted by normal [Zendesk requests limitation](https://developer.zendesk.com/rest_api/docs/support/usage_limits). The integration ideally should not run into Zendesk API limitations under normal usage.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
