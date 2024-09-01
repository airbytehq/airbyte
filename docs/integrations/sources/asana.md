# Asana

<HideInUI>

This page contains the setup guide and reference information for the [Asana](https://www.asana.com) source connector.

</HideInUI>

## Prerequisites

This connector supports **OAuth** and **Personal Access Tokens**. Please follow these [steps](https://developers.asana.com/docs/personal-access-token) to obtain Personal Access Token for your account.

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. Set the name for your source.
4. Authenticate using OAuth (recommended) or enter your `personal_access_token`.
5. Click **Set up source**.

#### Syncing Multiple Projects

If you have access to multiple projects, Airbyte will sync data related to all projects you have access to. The ability to filter to specific projects is not available at this time.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. Set the name for your source.
4. Enter your `personal_access_token`.
5. Click **Set up source**.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Asana source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Supported Streams

- [Attachments](https://developers.asana.com/docs/attachments)
- [Custom fields](https://developers.asana.com/docs/custom-fields)
- [Projects](https://developers.asana.com/docs/projects)
- [Portfolios](https://developers.asana.com/docs/portfolios)
- [PortfolioMemberships](https://developers.asana.com/reference/portfolio-memberships)
- [Sections](https://developers.asana.com/docs/sections)
- [Stories](https://developers.asana.com/docs/stories)
- [Tags](https://developers.asana.com/docs/tags)
- [Tasks](https://developers.asana.com/docs/tasks)
- [Teams](https://developers.asana.com/docs/teams)
- [Team Memberships](https://developers.asana.com/docs/team-memberships)
- [Users](https://developers.asana.com/docs/users)
- [Workspaces](https://developers.asana.com/docs/workspaces)

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

The connector is restricted by [Asana rate limits](https://developers.asana.com/docs/rate-limits).

### Troubleshooting

- If you encounter access errors while using **OAuth** authentication, please make sure you've followed this [Asana Article](https://developers.asana.com/docs/oauth).
- Check out common troubleshooting issues for the Asana source connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                           |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------|
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
