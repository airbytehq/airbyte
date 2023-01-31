# Freshdesk

This page guides you through the process of setting up the Freshdesk source connector.

## Prerequisites

To set up the Freshdesk source connector, you'll need the Freshdesk [domain URL](https://support.freshdesk.com/en/support/solutions/articles/50000004704-customizing-your-helpdesk-url) and the [API key](https://support.freshdesk.com/support/solutions/articles/215517).

## Set up the Freshdesk connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Freshdesk** from the Source type dropdown.
4. Enter the name for the Freshdesk connector.
5. For **Domain**, enter your [Freshdesk domain URL](https://support.freshdesk.com/en/support/solutions/articles/50000004704-customizing-your-helpdesk-url).
6. For **API Key**, enter your [Freshdesk API key](https://support.freshdesk.com/support/solutions/articles/215517).
7. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
8. For **Requests per minute**, enter the number of requests per minute that this source allowed to use. The Freshdesk rate limit is 50 requests per minute per app per account.
9. Click **Set up source**.

## Supported sync modes 

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

Several output streams are available from this source:

* [Agents](https://developers.freshdesk.com/api/#agents)
* [Business Hours](https://developers.freshdesk.com/api/#business-hours)
* [Canned Responses](https://developers.freshdesk.com/api/#canned-responses)
* [Canned Response Folders](https://developers.freshdesk.com/api/#list_all_canned_response_folders)
* [Companies](https://developers.freshdesk.com/api/#companies)
* [Contacts](https://developers.freshdesk.com/api/#contacts) \(Native Incremental Sync\)
* [Conversations](https://developers.freshdesk.com/api/#conversations)
* [Discussion Categories](https://developers.freshdesk.com/api/#category_attributes)
* [Discussion Comments](https://developers.freshdesk.com/api/#comment_attributes)
* [Discussion Forums](https://developers.freshdesk.com/api/#forum_attributes)
* [Discussion Topics](https://developers.freshdesk.com/api/#topic_attributes)
* [Email Configs](https://developers.freshdesk.com/api/#email-configs)
* [Email Mailboxes](https://developers.freshdesk.com/api/#email-mailboxes)
* [Groups](https://developers.freshdesk.com/api/#groups)
* [Products](https://developers.freshdesk.com/api/#products)
* [Roles](https://developers.freshdesk.com/api/#roles)
* [Satisfaction Ratings](https://developers.freshdesk.com/api/#satisfaction-ratings)
* [Scenario Automations](https://developers.freshdesk.com/api/#scenario-automations)
* [Settings](https://developers.freshdesk.com/api/#settings)
* [Skills](https://developers.freshdesk.com/api/#skills)
* [SLA Policies](https://developers.freshdesk.com/api/#sla-policies)
* [Solution Articles](https://developers.freshdesk.com/api/#solution_article_attributes)
* [Solution Categories](https://developers.freshdesk.com/api/#solution_category_attributes)
* [Solution Folders](https://developers.freshdesk.com/api/#solution_folder_attributes)
* [Surveys](https://developers.freshdesk.com/api/#surveys)
* [Tickets](https://developers.freshdesk.com/api/#tickets) \(Native Incremental Sync\)
* [Ticket Fields](https://developers.freshdesk.com/api/#ticket-fields)
* [Time Entries](https://developers.freshdesk.com/api/#time-entries)

## Performance considerations

The Freshdesk connector should not run into Freshdesk API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                               |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------|
| 2.0.1   | 2023-01-27 | [21888](https://github.com/airbytehq/airbyte/pull/21888) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 2.0.0   | 2022-12-20 | [20416](https://github.com/airbytehq/airbyte/pull/20416) | Fix `SlaPolicies` stream schema                                                       |
| 1.0.0   | 2022-11-16 | [19496](https://github.com/airbytehq/airbyte/pull/19496) | Fix `Contacts` stream schema                                                          |
| 0.3.8   | 2022-11-11 | [19349](https://github.com/airbytehq/airbyte/pull/19349) | Do not rely on response.json() when deciding to retry a request                       |
| 0.3.7   | 2022-11-03 | [18397](https://github.com/airbytehq/airbyte/pull/18397) | Fix base url for v2 API.                                                              |
| 0.3.6   | 2022-09-29 | [17410](https://github.com/airbytehq/airbyte/pull/17410) | Migrate to per-stream states.                                                         |
| 0.3.5   | 2022-09-27 | [17249](https://github.com/airbytehq/airbyte/pull/17249) | Added nullable to all stream schemas, added transformation into declared schema types |
| 0.3.4   | 2022-09-27 | [17243](https://github.com/airbytehq/airbyte/pull/17243) | Fixed the issue, when selected stream is not available due to Subscription Plan       |
| 0.3.3   | 2022-08-06 | [15378](https://github.com/airbytehq/airbyte/pull/15378) | Allow backward compatibility for input configuration                                  |
| 0.3.2   | 2022-06-23 | [14049](https://github.com/airbytehq/airbyte/pull/14049) | Update parsing of start_date                                                          |
| 0.3.1   | 2022-06-03 | [13332](https://github.com/airbytehq/airbyte/pull/13332) | Add new streams                                                                       |
| 0.3.0   | 2022-05-30 | [12334](https://github.com/airbytehq/airbyte/pull/12334) | Implement with latest CDK                                                             |
| 0.2.11  | 2021-12-14 | [8682](https://github.com/airbytehq/airbyte/pull/8682)   | Migrate to the CDK                                                                    |
| 0.2.10  | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)   | Update connector fields title/description                                             |
| 0.2.9   | 2021-11-16 | [8017](https://github.com/airbytehq/airbyte/pull/8017)   | Bugfix an issue that caused the connector to not sync more than 50000 contacts        |
| 0.2.8   | 2021-10-28 | [7486](https://github.com/airbytehq/airbyte/pull/7486)   | Include "requester" and "stats" fields in "tickets" stream                            |
| 0.2.7   | 2021-10-13 | [6442](https://github.com/airbytehq/airbyte/pull/6442)   | Add start_date parameter to specification from which to start pulling data.           |
