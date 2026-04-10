# Freshdesk

This page guides you through setting up the Freshdesk source connector.

## Prerequisites

To set up the Freshdesk source connector, you need:

- Your Freshdesk [domain URL](https://support.freshdesk.com/en/support/solutions/articles/50000004704-customizing-your-helpdesk-url) in the format `youraccount.freshdesk.com`.
- A Freshdesk [API key](https://support.freshdesk.com/support/solutions/articles/215517). To find your API key, log in to Freshdesk, click your profile picture, select **Profile Settings**, and click **View API key**.

## Set up the Freshdesk connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to your Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Freshdesk** from the **Source type** dropdown.
4. Enter a name for the Freshdesk connector.
5. For **Domain**, enter your Freshdesk domain in the format `youraccount.freshdesk.com`.
6. For **API Key**, enter your [Freshdesk API key](https://support.freshdesk.com/support/solutions/articles/215517).
7. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The connector replicates data created on and after this date. If not set, the connector retrieves only the last 30 days of ticket data.
8. For **Requests per minute**, optionally enter the number of requests per minute to allow. See [Performance considerations](#performance-considerations) for rate limits by plan.
9. For **Rate Limit Plan**, optionally select your Freshdesk plan to apply plan-specific rate limits for the Tickets and Contacts endpoints. If you select **Custom Plan**, enter your custom rate limits. If not set, the connector uses a default of 50 requests per minute.
10. For **Lookback Window**, optionally specify a number of days to re-read data from the current stream state for the **Satisfaction Ratings** stream. This captures updates to existing ratings after their initial creation. Records updated before the lookback window are not re-synced. The default is 14 days.
11. For **Number of Concurrent Workers**, optionally set the number of concurrent threads for syncing. Higher values speed up syncs but increase API rate limit usage. The default is 4, with a minimum of 2 and maximum of 16. Adjust based on your Freshdesk plan's rate limits.
12. Click **Set up source**.

## Supported sync modes

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

This source outputs the following streams:

- [Agents](https://developers.freshdesk.com/api/#agents)
- [Business Hours](https://developers.freshdesk.com/api/#business-hours)
- [Canned Responses](https://developers.freshdesk.com/api/#canned-responses)
- [Canned Response Folders](https://developers.freshdesk.com/api/#list_all_canned_response_folders)
- [Companies](https://developers.freshdesk.com/api/#companies)
- [Contacts](https://developers.freshdesk.com/api/#contacts) (incremental)
- [Conversations](https://developers.freshdesk.com/api/#conversations)
- [Discussion Categories](https://developers.freshdesk.com/api/#category_attributes)
- [Discussion Comments](https://developers.freshdesk.com/api/#comment_attributes)
- [Discussion Forums](https://developers.freshdesk.com/api/#forum_attributes)
- [Discussion Topics](https://developers.freshdesk.com/api/#topic_attributes)
- [Email Configs](https://developers.freshdesk.com/api/#email-configs)
- [Email Mailboxes](https://developers.freshdesk.com/api/#email-mailboxes)
- [Groups](https://developers.freshdesk.com/api/#groups)
- [Products](https://developers.freshdesk.com/api/#products)
- [Roles](https://developers.freshdesk.com/api/#roles)
- [Satisfaction Ratings](https://developers.freshdesk.com/api/#satisfaction-ratings)
- [Scenario Automations](https://developers.freshdesk.com/api/#scenario-automations)
- [Settings](https://developers.freshdesk.com/api/#settings)
- [Skills](https://developers.freshdesk.com/api/#skills)
- [SLA Policies](https://developers.freshdesk.com/api/#sla-policies)
- [Solution Articles](https://developers.freshdesk.com/api/#solution_article_attributes)
- [Solution Categories](https://developers.freshdesk.com/api/#solution_category_attributes)
- [Solution Folders](https://developers.freshdesk.com/api/#solution_folder_attributes)
- [Surveys](https://developers.freshdesk.com/api/#surveys)
- [Tickets](https://developers.freshdesk.com/api/#tickets) (incremental)
- [Ticket Fields](https://developers.freshdesk.com/api/#ticket-fields)
- [Time Entries](https://developers.freshdesk.com/api/#time-entries)

## Performance considerations

Freshdesk API rate limits depend on your plan. The connector automatically retries rate-limited requests using the `Retry-After` header.

| Plan | Calls per minute | Tickets list | Contacts list |
| :--------- | :--------------- | :----------- | :------------ |
| Free | 50 | 50 | 50 |
| Growth | 200 | 20 | 20 |
| Pro | 400 | 100 | 100 |
| Enterprise | 700 | 200 | 200 |

For more details, see [Freshdesk API rate limits](https://support.freshdesk.com/support/solutions/articles/225439-what-are-the-rate-limits-for-the-api-calls-to-freshdesk-).

To optimize sync performance, select your **Rate Limit Plan** in the connector configuration and adjust the **Number of Concurrent Workers** setting. Higher concurrency speeds up syncs but consumes more of your rate limit budget. If you experience rate limit errors, reduce the number of concurrent workers or select a plan with higher limits.

If you don't set a **Start Date**, the connector retrieves only the last 30 days of ticket data. For more information, see the [Freshdesk API ticket listing documentation](https://developers.freshdesk.com/api/#list_all_tickets).

Some streams require specific Freshdesk subscription plans. If a stream is unavailable on your plan, the connector skips it during sync.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                               |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| 3.2.14-rc.1 | 2026-04-10 | [76202](https://github.com/airbytehq/airbyte/pull/76202) | Add concurrency_level and num_workers for concurrency tuning |
| 3.2.13 | 2026-03-31 | [75719](https://github.com/airbytehq/airbyte/pull/75719) | Update dependencies |
| 3.2.12 | 2026-03-24 | [74647](https://github.com/airbytehq/airbyte/pull/74647) | Update dependencies |
| 3.2.11 | 2026-03-03 | [74188](https://github.com/airbytehq/airbyte/pull/74188) | Update dependencies |
| 3.2.10 | 2026-02-17 | [73400](https://github.com/airbytehq/airbyte/pull/73400) | Update dependencies |
| 3.2.9 | 2026-02-10 | [72557](https://github.com/airbytehq/airbyte/pull/72557) | Update dependencies |
| 3.2.8 | 2026-01-20 | [71949](https://github.com/airbytehq/airbyte/pull/71949) | Update dependencies |
| 3.2.7 | 2026-01-14 | [71629](https://github.com/airbytehq/airbyte/pull/71629) | Update dependencies |
| 3.2.6 | 2025-12-18 | [70595](https://github.com/airbytehq/airbyte/pull/70595) | Update dependencies |
| 3.2.5 | 2025-11-25 | [70016](https://github.com/airbytehq/airbyte/pull/70016) | Update dependencies |
| 3.2.4 | 2025-11-18 | [69435](https://github.com/airbytehq/airbyte/pull/69435) | Update dependencies |
| 3.2.3 | 2025-10-29 | [68786](https://github.com/airbytehq/airbyte/pull/68786) | Update dependencies |
| 3.2.2 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 3.2.1 | 2025-10-21 | [68420](https://github.com/airbytehq/airbyte/pull/68420) | Update dependencies |
| 3.2.0 | 2025-10-14 | [68089](https://github.com/airbytehq/airbyte/pull/68089) | Complete progressive rollout |
| 3.2.0-rc.2 | 2025-10-09 | [67109](https://github.com/airbytehq/airbyte/pull/67109) | Migrate to CDK v7 |
| 3.2.0-rc.1 | 2025-03-12 | [54687](https://github.com/airbytehq/airbyte/pull/54687) | Migrate to Manifest-only |
| 3.1.3 | 2025-02-26 | [54696](https://github.com/airbytehq/airbyte/pull/54696) | Update requests-mock dependency version |
| 3.1.2 | 2025-01-11 | [43887](https://github.com/airbytehq/airbyte/pull/43887) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 3.1.1 | 2024-06-06 | [39231](https://github.com/airbytehq/airbyte/pull/39231) | [autopull] Upgrade base image to v1.2.2 |
| 3.1.0 | 2024-03-12 | [35699](https://github.com/airbytehq/airbyte/pull/35699) | Migrate to low-code |
| 3.0.7 | 2024-02-12 | [35187](https://github.com/airbytehq/airbyte/pull/35187) | Manage dependencies with Poetry. |
| 3.0.6 | 2024-01-10 | [34101](https://github.com/airbytehq/airbyte/pull/34101) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 3.0.5 | 2023-11-30 | [33000](https://github.com/airbytehq/airbyte/pull/33000) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 3.0.4 | 2023-06-24 | [27680](https://github.com/airbytehq/airbyte/pull/27680) | Fix formatting |
| 3.0.3 | 2023-06-02 | [26978](https://github.com/airbytehq/airbyte/pull/26978) | Skip the stream if subscription level had changed during sync |
| 3.0.2 | 2023-02-06 | [21970](https://github.com/airbytehq/airbyte/pull/21970) | Enable availability strategy for all streams |
| 3.0.0 | 2023-01-31 | [22164](https://github.com/airbytehq/airbyte/pull/22164) | Rename nested `business_hours` table to `working_hours` |
| 2.0.1 | 2023-01-27 | [21888](https://github.com/airbytehq/airbyte/pull/21888) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 2.0.0 | 2022-12-20 | [20416](https://github.com/airbytehq/airbyte/pull/20416) | Fix `SlaPolicies` stream schema |
| 1.0.0 | 2022-11-16 | [19496](https://github.com/airbytehq/airbyte/pull/19496) | Fix `Contacts` stream schema |
| 0.3.8 | 2022-11-11 | [19349](https://github.com/airbytehq/airbyte/pull/19349) | Do not rely on response.json() when deciding to retry a request |
| 0.3.7 | 2022-11-03 | [18397](https://github.com/airbytehq/airbyte/pull/18397) | Fix base url for v2 API. |
| 0.3.6 | 2022-09-29 | [17410](https://github.com/airbytehq/airbyte/pull/17410) | Migrate to per-stream states. |
| 0.3.5 | 2022-09-27 | [17249](https://github.com/airbytehq/airbyte/pull/17249) | Added nullable to all stream schemas, added transformation into declared schema types |
| 0.3.4 | 2022-09-27 | [17243](https://github.com/airbytehq/airbyte/pull/17243) | Fixed the issue, when selected stream is not available due to Subscription Plan |
| 0.3.3 | 2022-08-06 | [15378](https://github.com/airbytehq/airbyte/pull/15378) | Allow backward compatibility for input configuration |
| 0.3.2 | 2022-06-23 | [14049](https://github.com/airbytehq/airbyte/pull/14049) | Update parsing of start_date |
| 0.3.1 | 2022-06-03 | [13332](https://github.com/airbytehq/airbyte/pull/13332) | Add new streams |
| 0.3.0 | 2022-05-30 | [12334](https://github.com/airbytehq/airbyte/pull/12334) | Implement with latest CDK |
| 0.2.11 | 2021-12-14 | [8682](https://github.com/airbytehq/airbyte/pull/8682) | Migrate to the CDK |
| 0.2.10 | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description |
| 0.2.9 | 2021-11-16 | [8017](https://github.com/airbytehq/airbyte/pull/8017) | Bugfix an issue that caused the connector to not sync more than 50000 contacts |
| 0.2.8 | 2021-10-28 | [7486](https://github.com/airbytehq/airbyte/pull/7486) | Include "requester" and "stats" fields in "tickets" stream |
| 0.2.7 | 2021-10-13 | [6442](https://github.com/airbytehq/airbyte/pull/6442) | Add start_date parameter to specification from which to start pulling data. |

</details>
