# Goldcast

This page contains the setup guide and reference information for the Goldcast source connector.

## Prerequisites

- A [Goldcast Pro plan](https://www.goldcast.io/pricing) or higher. The Starter plan does not allow API access.
- API tokens enabled for your Goldcast organization. Goldcast disables tokens by default, so if your plan includes API access, contact Goldcast support to turn them on.
- A Goldcast API token. Follow [Goldcast's guide](https://help.goldcast.io/hc/en-us/articles/22931655725723-How-To-Create-an-API-Token-in-Goldcast) to create one in Goldcast Studio under **Settings** > **Tokens**. If your organization uses Goldcast Teams, only organization admins can create tokens. Goldcast shows the token value only once, so copy it when you create it. The token is case-sensitive.

## Setup guide

<!-- env:cloud -->

### For Airbyte Cloud

To set up Goldcast as a source in Airbyte Cloud:

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Goldcast** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **Access Key** (the API token you created in Goldcast).
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source

To set up Goldcast as a source in Airbyte Open Source:

1. Log in to your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Goldcast** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **Access Key** (the API token you created in Goldcast).
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

## Supported Sync Modes

The Goldcast source connector supports the following [sync modes](/platform/using-airbyte/core-concepts/sync-modes/):

- [Full Refresh - Overwrite](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

Incremental modes are not supported because the Goldcast API does not expose a cursor field, such as a modified-at timestamp, that the connector can filter on.

## Supported Streams

The Goldcast source connector can sync the following streams. See the [Goldcast API documentation](https://apidocs.goldcast.io/) for details on each endpoint.

| Stream | Description |
| :--- | :--- |
| [organizations](https://apidocs.goldcast.io/#tag/Organization/operation/List%20organization) | Your Goldcast organization and its workspace settings. |
| [events](https://apidocs.goldcast.io/#tag/Event/operation/List%20events) | All events of every type (webinars, conferences, and so on). |
| [event_members](https://apidocs.goldcast.io/#tag/Event-members/operation/List%20event%20members) | Registrants and attendees of each event. Child of `events`. See [The `props` field](#the-props-field-in-event_members). |
| [webinars](https://apidocs.goldcast.io/#tag/Webinars/operation/Retrieve%20webinars) | Webinar settings for each event. Child of `events`, limited to events whose type is `Webinar`. |
| [tracks](https://apidocs.goldcast.io/#tag/Tracks/operation/List%20tracks) | Tracks associated with your events. |
| [agenda_items](https://apidocs.goldcast.io/#tag/Agenda-item/operation/List%20agenda%20item) | Agenda items associated with your events. |
| [discussion_groups](https://apidocs.goldcast.io/#tag/Discussion-groups/operation/List%20discussion%20groups) | Discussion groups associated with your events. |

The connector requests list endpoints with `limit`/`offset` pagination, 100 records per page. The `webinars` stream is scoped to webinar-type events because the Goldcast webinars endpoint returns an error for other event types.

### The `props` field in `event_members`

Each `event_members` record has a `props` object that holds the registration form fields for that registrant, such as UTM parameters or job title. Goldcast lets every workspace define its own registration fields, so the connector doesn't declare a fixed set of properties inside `props`. It syncs `props` as a schemaless object that contains whatever fields your workspace collects.

How `props` lands in your destination depends on the destination:

- Database and data lake destinations store `props` as a single JSON value with every field intact.
- S3 and GCS destinations writing Avro or Parquet files store `props` as a JSON string. To read individual fields, parse that string in your query engine instead of addressing `props.<field>` as a nested column.

Before version 1.0.0, the connector declared eleven fixed fields inside `props`, and Avro and Parquet files silently dropped any other registration field. If you're upgrading from an earlier version, see the [migration guide](goldcast-migrations).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request                                             | Subject                                                                                                                              |
|:---------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.0 | 2026-09-15 | [82770](https://github.com/airbytehq/airbyte/pull/82770) | Make `event_members` `props` schemaless so every workspace-defined registration field is preserved on S3/GCS Avro and Parquet destinations; see the [migration guide](https://docs.airbyte.com/integrations/sources/goldcast-migrations) |
| 0.2.26 | 2026-08-20 | [83237](https://github.com/airbytehq/airbyte/pull/83237) | Fix connector broken by Goldcast's API changes: list streams now request `limit`/`offset` pagination and extract records from the `results` envelope, and the `webinars` stream is scoped to webinar-type events only to avoid errors on other event types |
| 0.2.25 | 2026-06-02 | [78729](https://github.com/airbytehq/airbyte/pull/78729) | Update dependencies |
| 0.2.24 | 2025-05-10 | [59909](https://github.com/airbytehq/airbyte/pull/59909) | Update dependencies |
| 0.2.23 | 2025-05-03 | [59258](https://github.com/airbytehq/airbyte/pull/59258) | Update dependencies |
| 0.2.22 | 2025-04-26 | [58791](https://github.com/airbytehq/airbyte/pull/58791) | Update dependencies |
| 0.2.21 | 2025-04-19 | [58182](https://github.com/airbytehq/airbyte/pull/58182) | Update dependencies |
| 0.2.20 | 2025-04-12 | [57670](https://github.com/airbytehq/airbyte/pull/57670) | Update dependencies |
| 0.2.19 | 2025-04-05 | [57206](https://github.com/airbytehq/airbyte/pull/57206) | Update dependencies |
| 0.2.18 | 2025-03-29 | [56472](https://github.com/airbytehq/airbyte/pull/56472) | Update dependencies |
| 0.2.17 | 2025-03-22 | [55958](https://github.com/airbytehq/airbyte/pull/55958) | Update dependencies |
| 0.2.16 | 2025-03-08 | [55274](https://github.com/airbytehq/airbyte/pull/55274) | Update dependencies |
| 0.2.15 | 2025-03-01 | [54953](https://github.com/airbytehq/airbyte/pull/54953) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54439](https://github.com/airbytehq/airbyte/pull/54439) | Update dependencies |
| 0.2.13 | 2025-02-15 | [53762](https://github.com/airbytehq/airbyte/pull/53762) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53338](https://github.com/airbytehq/airbyte/pull/53338) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52838](https://github.com/airbytehq/airbyte/pull/52838) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52325](https://github.com/airbytehq/airbyte/pull/52325) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51636](https://github.com/airbytehq/airbyte/pull/51636) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51103](https://github.com/airbytehq/airbyte/pull/51103) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50571](https://github.com/airbytehq/airbyte/pull/50571) | Update dependencies |
| 0.2.6 | 2024-12-21 | [49998](https://github.com/airbytehq/airbyte/pull/49998) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49480](https://github.com/airbytehq/airbyte/pull/49480) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49158](https://github.com/airbytehq/airbyte/pull/49158) | Update dependencies |
| 0.2.3 | 2024-11-04 | [48148](https://github.com/airbytehq/airbyte/pull/48148) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47875](https://github.com/airbytehq/airbyte/pull/47875) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47533](https://github.com/airbytehq/airbyte/pull/47533) | Update dependencies |
| 0.2.0 | 2024-08-22 | [44568](https://github.com/airbytehq/airbyte/pull/44568) | Refactor connector to manifest-only format |
| 0.1.8 | 2024-08-12 | [43804](https://github.com/airbytehq/airbyte/pull/43804) | Update dependencies |
| 0.1.7 | 2024-08-10 | [43522](https://github.com/airbytehq/airbyte/pull/43522) | Update dependencies |
| 0.1.6 | 2024-08-03 | [43284](https://github.com/airbytehq/airbyte/pull/43284) | Update dependencies |
| 0.1.5 | 2024-07-27 | [42616](https://github.com/airbytehq/airbyte/pull/42616) | Update dependencies |
| 0.1.4 | 2024-07-20 | [42237](https://github.com/airbytehq/airbyte/pull/42237) | Update dependencies |
| 0.1.3 | 2024-07-13 | [41806](https://github.com/airbytehq/airbyte/pull/41806) | Update dependencies |
| 0.1.2 | 2024-07-10 | [41406](https://github.com/airbytehq/airbyte/pull/41406) | Update dependencies |
| 0.1.1 | 2024-07-09 | [41263](https://github.com/airbytehq/airbyte/pull/41263) | Update dependencies |
| 0.1.0 | 2024-06-26 | [38786](https://github.com/airbytehq/airbyte/pull/38786) | New Source: Goldcast |
</details>
