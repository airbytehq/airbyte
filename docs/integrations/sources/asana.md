# Asana

<HideInUI>

This page contains the setup guide and reference information for the [Asana](https://www.asana.com) source connector.

</HideInUI>

## Prerequisites

To use the Asana source connector, you need:

- An Asana account with access to the workspaces, projects, tasks, portfolios, and other resources you want to sync.
- One of the following authentication methods:
  - **OAuth**. Recommended for Airbyte Cloud.
  - **Personal Access Token**. To create a token, follow Asana's [personal access token instructions](https://developers.asana.com/docs/personal-access-token).

The connector can only sync data the authenticated Asana user can access. If the authenticated user has a view-only license or limited project access in Asana, the connector has the same limitations.

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**.
3. Click **+ New source**.
4. Select **Asana** from the list of available sources.
5. Enter a **Source name**.
6. Authenticate using OAuth, or enter a personal access token.
7. Optionally, enter **Organization Export IDs** if you want to sync specific organization exports.
8. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**.
3. Click **+ New source**.
4. Select **Asana** from the list of available sources.
5. Enter a **Source name**.
6. Enter a personal access token.
7. Optionally, enter **Organization Export IDs** if you want to sync specific organization exports.
8. Click **Set up source**.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Asana source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Namespaces | No |

## Supported streams

The Asana source connector supports these streams:

| Stream | Description |
| :--- | :--- |
| [`attachments`](https://developers.asana.com/reference/attachments) | Attachment details for attachments on synced projects and tasks. |
| [`attachments_compact`](https://developers.asana.com/reference/attachments) | Compact attachment records for synced projects and tasks. |
| [`custom_fields`](https://developers.asana.com/reference/custom-fields) | Custom field definitions in each accessible workspace. |
| [`events`](https://developers.asana.com/reference/events) | Events for synced projects and tasks. |
| [`organization_exports`](https://developers.asana.com/reference/organization-exports) | Organization export requests for the export IDs you provide in the source configuration. |
| [`portfolio_items`](https://developers.asana.com/reference/getitemsforportfolio) | Projects and portfolios contained in each synced portfolio. |
| [`portfolios`](https://developers.asana.com/reference/portfolios) | Portfolio details for synced portfolios. |
| [`portfolios_compact`](https://developers.asana.com/reference/portfolios) | Compact portfolio records for each synced workspace and user. |
| [`portfolios_memberships`](https://developers.asana.com/reference/portfolio-memberships) | Portfolio memberships for synced portfolios. |
| [`projects`](https://developers.asana.com/reference/projects) | Projects in each accessible workspace. |
| [`sections`](https://developers.asana.com/reference/sections) | Section details for synced project sections. |
| [`sections_compact`](https://developers.asana.com/reference/sections) | Compact section records for synced projects. |
| [`stories`](https://developers.asana.com/reference/stories) | Story details for synced task stories. |
| [`stories_compact`](https://developers.asana.com/reference/stories) | Compact story records for synced tasks. |
| [`tags`](https://developers.asana.com/reference/tags) | Tags in each accessible workspace. |
| [`tasks`](https://developers.asana.com/reference/tasks) | Tasks in synced projects. |
| [`team_memberships`](https://developers.asana.com/reference/team-memberships) | Team membership records for synced teams. |
| [`teams`](https://developers.asana.com/reference/teams) | Teams in each accessible organization workspace. |
| [`users`](https://developers.asana.com/reference/users) | Users in each accessible workspace. |
| [`workspaces`](https://developers.asana.com/reference/workspaces) | Workspaces the authenticated user can access. |

## Data type map

| Integration Type         | Airbyte Type |
| :----------------------- | :----------- |
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Asana connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Asana applies rate limits per authorization token. Asana's standard limit is 150 requests per minute for free domains and 1,500 requests per minute for paid domains. The connector retries `429 Too Many Requests` responses using Asana's `Retry-After` header.

If you continue to see rate limit errors, reduce the **Number of concurrent threads** in the source configuration.

#### Syncing multiple projects

Airbyte syncs data from all Asana projects the authenticated user can access. The connector doesn't support filtering to specific projects.

#### Organization exports

The `organization_exports` stream syncs only the organization export IDs listed in the source configuration. To sync this stream, first create organization export requests in Asana and then enter the returned export IDs in **Organization Export IDs**.

Asana's organization export endpoints are only available to Enterprise organization service accounts. To sync organization exports, authenticate with an Asana service account token.

### Troubleshooting

- If you encounter access errors while using OAuth, make sure your Asana OAuth app is configured correctly. For more information, see Asana's [OAuth documentation](https://developers.asana.com/docs/oauth).
- If the connector returns permissions errors for some streams, confirm that the authenticated Asana user can view those resources in Asana.
- For other troubleshooting topics, see the [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Reference

This connector uses the [Asana REST API](https://developers.asana.com/reference/rest-api-reference). All API requests use the `https://app.asana.com/api/1.0` endpoint.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| :--- | :---: | :--- |
| `credentials.option_title` | Yes | Authentication method. Valid values are `OAuth Credentials` and `PAT Credentials`. |
| `credentials.client_id` | Required for OAuth | Client ID for the Asana OAuth app. |
| `credentials.client_secret` | Required for OAuth | Client secret for the Asana OAuth app. |
| `credentials.refresh_token` | Required for OAuth | Refresh token returned by the Asana OAuth flow. |
| `credentials.personal_access_token` | Required for personal access token authentication | Asana personal access token. For organization exports, use an Asana service account token. |
| `organization_export_ids` | No | List of Asana organization export IDs to sync in the `organization_exports` stream. |
| `num_workers` | No | Number of concurrent threads to use for the sync. Valid values are `1` through `25`. Defaults to `10`. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.6.0-rc.2 | 2026-05-14 | [78082](https://github.com/airbytehq/airbyte/pull/78082) | Fix projects stream HTTP 400 after CDK v7 upgrade |
| 1.6.0-rc.1 | 2026-04-27 | [76390](https://github.com/airbytehq/airbyte/pull/76390) | chore(source-asana): bump airbyte-cdk from ^6 to ^7.13.0 |
| 1.5.3 | 2026-04-13 | [76276](https://github.com/airbytehq/airbyte/pull/76276) | Rename "concurrent workers" to "concurrent threads" in connector spec |
| 1.5.2 | 2026-04-07 | [76100](https://github.com/airbytehq/airbyte/pull/76100) | Improve error messages for HTTP 400, 401, and 429 responses with granular failure type classification |
| 1.5.1 | 2025-12-08 | [70445](https://github.com/airbytehq/airbyte/pull/70445) | Fix `organization_export_ids` spec to properly define array items type |
| 1.5.0 | 2025-05-05 | [59224](https://github.com/airbytehq/airbyte/pull/59224) | Adds `portfolio_items` stream to sync items (such as projects and portfolios) in each portfolio ([API reference](https://developers.asana.com/reference/getitemsforportfolio)) |
| 1.4.0 | 2025-04-24 | [58594](https://github.com/airbytehq/airbyte/pull/58594) | Adds `actual_time_minute` field to the `task` stream |
| 1.3.10 | 2025-02-15 | [53891](https://github.com/airbytehq/airbyte/pull/53891) | Update dependencies |
| 1.3.9 | 2025-02-08 | [53394](https://github.com/airbytehq/airbyte/pull/53394) | Update dependencies |
| 1.3.8 | 2025-02-01 | [52882](https://github.com/airbytehq/airbyte/pull/52882) | Update dependencies |
| 1.3.7 | 2025-01-25 | [52216](https://github.com/airbytehq/airbyte/pull/52216) | Update dependencies |
| 1.3.6 | 2025-01-18 | [51750](https://github.com/airbytehq/airbyte/pull/51750) | Update dependencies |
| 1.3.5 | 2025-01-11 | [51246](https://github.com/airbytehq/airbyte/pull/51246) | Update dependencies |
| 1.3.4 | 2025-01-04 | [50915](https://github.com/airbytehq/airbyte/pull/50915) | Update dependencies |
| 1.3.3 | 2024-12-28 | [50442](https://github.com/airbytehq/airbyte/pull/50442) | Update dependencies |
| 1.3.2 | 2024-12-21 | [50195](https://github.com/airbytehq/airbyte/pull/50195) | Update dependencies |
| 1.3.1 | 2024-12-14 | [48966](https://github.com/airbytehq/airbyte/pull/48966) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.3.0 | 2024-12-06 | [48712](https://github.com/airbytehq/airbyte/pull/48712) | Upgrade to process full refresh and non-incremental substreams using concurrent CDK |
| 1.2.14 | 2024-11-04 | [48175](https://github.com/airbytehq/airbyte/pull/48175) | Update dependencies |
| 1.2.13 | 2024-10-28 | [47026](https://github.com/airbytehq/airbyte/pull/47026) | Update dependencies |
| 1.2.12 | 2024-10-12 | [46825](https://github.com/airbytehq/airbyte/pull/46825) | Update dependencies |
| 1.2.11 | 2024-10-05 | [46501](https://github.com/airbytehq/airbyte/pull/46501) | Update dependencies |
| 1.2.10 | 2024-09-28 | [46166](https://github.com/airbytehq/airbyte/pull/46166) | Update dependencies |
| 1.2.9 | 2024-09-21 | [45754](https://github.com/airbytehq/airbyte/pull/45754) | Update dependencies |
| 1.2.8 | 2024-09-14 | [45547](https://github.com/airbytehq/airbyte/pull/45547) | Update dependencies |
| 1.2.7 | 2024-09-07 | [45277](https://github.com/airbytehq/airbyte/pull/45277) | Update dependencies |
| 1.2.6 | 2024-08-31 | [44970](https://github.com/airbytehq/airbyte/pull/44970) | Update dependencies |
| 1.2.5 | 2024-08-24 | [44722](https://github.com/airbytehq/airbyte/pull/44722) | Update dependencies |
| 1.2.4 | 2024-08-17 | [44275](https://github.com/airbytehq/airbyte/pull/44275) | Update dependencies |
| 1.2.3 | 2024-08-12 | [43807](https://github.com/airbytehq/airbyte/pull/43807) | Update dependencies |
| 1.2.2 | 2024-08-10 | [43532](https://github.com/airbytehq/airbyte/pull/43532) | Update dependencies |
| 1.2.1 | 2024-08-03 | [43079](https://github.com/airbytehq/airbyte/pull/43079) | Update dependencies |
| 1.2.0 | 2024-07-27 | [42856](https://github.com/airbytehq/airbyte/pull/42856) | Add task & target data to stories compact stream |
| 1.1.1 | 2024-07-27 | [42801](https://github.com/airbytehq/airbyte/pull/42801) | Update dependencies |
| 1.1.0 | 2024-07-24 | [42488](https://github.com/airbytehq/airbyte/pull/42488) | Add task data to stories stream |
| 1.0.9 | 2024-07-20 | [42144](https://github.com/airbytehq/airbyte/pull/42144) | Update dependencies |
| 1.0.8 | 2024-07-13 | [41839](https://github.com/airbytehq/airbyte/pull/41839) | Update dependencies |
| 1.0.7 | 2024-07-10 | [41573](https://github.com/airbytehq/airbyte/pull/41573) | Update dependencies |
| 1.0.6 | 2024-07-09 | [41142](https://github.com/airbytehq/airbyte/pull/41142) | Update dependencies |
| 1.0.5 | 2024-07-06 | [40865](https://github.com/airbytehq/airbyte/pull/40865) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40392](https://github.com/airbytehq/airbyte/pull/40392) | Update dependencies |
| 1.0.3 | 2024-06-22 | [40092](https://github.com/airbytehq/airbyte/pull/40092) | Update dependencies |
| 1.0.2 | 2024-06-18 | [39551](https://github.com/airbytehq/airbyte/pull/39551) | Fix pagination from offset to cursor based, Increment airbyte_cdk to ^1 |
| 1.0.1 | 2024-06-06 | [39249](https://github.com/airbytehq/airbyte/pull/39249) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.0 | 2024-04-15 | [36697](https://github.com/airbytehq/airbyte/pull/36697) | Migrate to low code |
| 0.6.1 | 2023-11-13 | [31110](https://github.com/airbytehq/airbyte/pull/31110) | Fix hidden config access |
| 0.6.0 | 2023-11-03 | [31110](https://github.com/airbytehq/airbyte/pull/31110) | Add new stream Portfolio Memberships with Parent Portfolio |
| 0.5.0 | 2023-10-30 | [31114](https://github.com/airbytehq/airbyte/pull/31114) | Add Portfolios stream |
| 0.4.0 | 2023-10-24 | [31084](https://github.com/airbytehq/airbyte/pull/31084) | Add StoriesCompact stream |
| 0.3.0 | 2023-10-24 | [31634](https://github.com/airbytehq/airbyte/pull/31634) | Add OrganizationExports stream |
| 0.2.0 | 2023-10-17 | [31090](https://github.com/airbytehq/airbyte/pull/31090) | Add Attachments stream |
| 0.1.9 | 2023-10-16 | [31089](https://github.com/airbytehq/airbyte/pull/31089) | Add Events stream |
| 0.1.8 | 2023-10-16 | [31009](https://github.com/airbytehq/airbyte/pull/31009) | Add SectionsCompact stream |
| 0.1.7 | 2023-05-29 | [26716](https://github.com/airbytehq/airbyte/pull/26716) | Remove authSpecification from spec.json, use advancedAuth instead |
| 0.1.6 | 2023-05-26 | [26653](https://github.com/airbytehq/airbyte/pull/26653) | Fix order of authentication methods |
| 0.1.5 | 2022-11-16 | [19561](https://github.com/airbytehq/airbyte/pull/19561) | Added errors handling, updated SAT with new format |
| 0.1.4 | 2022-08-18 | [15749](https://github.com/airbytehq/airbyte/pull/15749) | Add cache to project stream |
| 0.1.3 | 2021-10-06 | [6832](https://github.com/airbytehq/airbyte/pull/6832) | Add oauth init flow parameters support |
| 0.1.2 | 2021-09-24 | [6402](https://github.com/airbytehq/airbyte/pull/6402) | Fix SAT tests: update schemas and invalid_config.json file |
| 0.1.1 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add entrypoint and bump version for connector |
| 0.1.0 | 2021-05-25 | [3510](https://github.com/airbytehq/airbyte/pull/3510) | New Source: Asana |

</details>

</HideInUI>
