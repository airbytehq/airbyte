# Sentry

This page contains the setup guide and reference information for the Sentry source connector.

## Prerequisites

To set up the Sentry source connector, you need:

- A Sentry [organization slug](https://docs.sentry.io/product/accounts/membership/)
- A [project slug](https://docs.sentry.io/product/projects/) in that organization
- A Sentry [authentication token](https://docs.sentry.io/api/auth/#auth-tokens) with the scopes required by the streams you sync

For Sentry SaaS, you can create an organization-wide token with a Sentry [internal integration](https://docs.sentry.io/integrations/integration-platform/internal-integration/). Configure the integration with read access for organizations, projects, and issues and events to sync every stream.

## Set up the Sentry connector in Airbyte

1. In Airbyte, select **Sources**, then select **New source**.
2. Select **Sentry**.
3. For **Authentication Tokens**, enter your Sentry authentication token.
4. For **Host Name**, keep `sentry.io` for Sentry SaaS, or enter the hostname of your self-hosted Sentry server without `https://` or a path. You can also use your Sentry SaaS [region-specific domain](https://docs.sentry.io/api/#choosing-the-right-api-base-domain), such as `us.sentry.io`, `us2.sentry.io`, or `de.sentry.io`.
5. For **Organization**, enter the organization slug.
6. For **Project**, enter the project slug. This setting determines which project the `events`, `issues`, and `project_detail` streams sync. Organization-level streams aren't limited to this project.
7. Optionally, for **Number of concurrent workers**, enter a value from 1 through 20. The default is 5.
8. Select **Set up source**.

## Supported sync modes

The Sentry source connector supports these [sync modes](/platform/using-airbyte/core-concepts/sync-modes):

- [Full Refresh - Overwrite](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

## Supported streams

| Stream | Data synced | Supported sync modes |
| :--- | :--- | :--- |
| [Events](https://docs.sentry.io/api/events/list-a-projects-error-events/) | Error events for the configured project | Full refresh, incremental |
| [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/) | Issues for the configured project | Full refresh, incremental |
| [Projects](https://docs.sentry.io/api/organizations/list-an-organizations-projects/) | Projects in the configured organization | Full refresh, incremental |
| [Project Detail](https://docs.sentry.io/api/projects/retrieve-a-project/) | Full details for the configured project | Full refresh |
| [All Projects Detail](https://docs.sentry.io/api/projects/retrieve-a-project/) | Full details for every project in the configured organization | Full refresh |
| [Releases](https://docs.sentry.io/api/releases/list-an-organizations-releases/) | Releases in the configured organization | Full refresh, incremental |

The `all_projects_detail` stream makes one project-detail request for every project returned by the organization-level list endpoint.

:::note Version 1.0.0

The `projects` stream now returns only projects in the configured organization. The `avatar`, `color`, `isInternal`, `isPublic`, `organization`, and `status` fields return `null` in this stream. Sync `all_projects_detail` to retrieve these fields for every project. For upgrade instructions, see the [Sentry migration guide](/integrations/sources/sentry-migrations).

:::

## Authentication token scopes

The authentication token must include the scopes required by the streams you sync. To sync every stream, grant `org:read`, `event:read`, and `project:read`.

| Stream              | Endpoint                                                          | Required scope             |
| :------------------ | :---------------------------------------------------------------- | :------------------------- |
| Events              | `GET /api/0/projects/{organization}/{project}/events/`            | `project:read`             |
| Issues              | `GET /api/0/projects/{organization}/{project}/issues/`            | `event:read`               |
| Projects            | `GET /api/0/organizations/{organization}/projects/`               | `org:read`                 |
| Project Detail      | `GET /api/0/projects/{organization}/{project}/`                   | `project:read`             |
| All Projects Detail | `GET /api/0/projects/{organization}/{project}/` (per org project) | `org:read`, `project:read` |
| Releases            | `GET /api/0/organizations/{organization}/releases/`               | `project:read`             |

If the token is missing a scope, the corresponding stream returns an HTTP 403 error. See the Sentry [permissions and scopes](https://docs.sentry.io/api/permissions/) reference for details.

## Limitations and troubleshooting

### Event retention

:::warning

Sentry SaaS retains error events for 30 or 90 days, depending on your plan. If you use Full Refresh - Overwrite, a sync replaces older destination records with only the events still available from Sentry. Use an append mode if you need to keep events beyond Sentry's [data retention period](https://docs.sentry.io/security-legal-pii/security/data-retention-periods/).

:::

### Rate limits

Sentry applies request and concurrency limits per caller and endpoint. The limits are returned in the `X-Sentry-Rate-Limit-*` response headers and can vary by endpoint. If syncs receive HTTP 429 responses, reduce **Number of concurrent workers**. See Sentry's [rate limit documentation](https://docs.sentry.io/api/ratelimits/).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.3 | 2026-07-21 | [82603](https://github.com/airbytehq/airbyte/pull/82603) | Update dependencies |
| 1.0.2 | 2026-07-14 | [82008](https://github.com/airbytehq/airbyte/pull/82008) | Update dependencies |
| 1.0.1 | 2026-07-13 | [81707](https://github.com/airbytehq/airbyte/pull/81707) | Scope the 1.0.0 breaking change to the `projects` stream and emphasize the risk of data loss in the migration guide |
| 1.0.0 | 2026-07-13 | [80190](https://github.com/airbytehq/airbyte/pull/80190) | Breaking: migrate the `projects` stream to the org-scoped endpoint (Sentry deprecated the legacy `/projects/` endpoint). The stream now returns only projects belonging to the configured organization, and no longer returns `avatar`, `color`, `isInternal`, `isPublic`, `organization`, `status`. Added the `all_projects_detail` stream, which returns full project details (including those six fields) for every project in the organization. See the [migration guide](/integrations/sources/sentry-migrations). |
| 0.9.27 | 2026-06-30 | [81219](https://github.com/airbytehq/airbyte/pull/81219) | Update dependencies |
| 0.9.26 | 2026-06-23 | [80622](https://github.com/airbytehq/airbyte/pull/80622) | Update dependencies |
| 0.9.25 | 2026-06-16 | [80036](https://github.com/airbytehq/airbyte/pull/80036) | Update dependencies |
| 0.9.24 | 2026-06-09 | [79482](https://github.com/airbytehq/airbyte/pull/79482) | Update dependencies |
| 0.9.23 | 2026-06-02 | [78975](https://github.com/airbytehq/airbyte/pull/78975) | Update dependencies |
| 0.9.22 | 2026-06-01 | [78537](https://github.com/airbytehq/airbyte/pull/78537) | Add user-configurable `num_workers` concurrency setting (default 5, tested optimal at 7) |
| 0.9.22-rc.2 | 2026-05-27 | [78468](https://github.com/airbytehq/airbyte/pull/78468) | Concurrency tuning iteration 2 — bump default_concurrency from 7 to 8 |
| 0.9.22-rc.1 | 2026-05-26 | [78444](https://github.com/airbytehq/airbyte/pull/78444) | Concurrency tuning — bump default_concurrency from 5 to 7 for progressive rollout |
| 0.9.21 | 2026-04-28 | [77407](https://github.com/airbytehq/airbyte/pull/77407) | Update dependencies |
| 0.9.20 | 2026-04-21 | [76772](https://github.com/airbytehq/airbyte/pull/76772) | Update dependencies |
| 0.9.19 | 2026-03-31 | [75797](https://github.com/airbytehq/airbyte/pull/75797) | Update dependencies |
| 0.9.18 | 2026-03-24 | [75330](https://github.com/airbytehq/airbyte/pull/75330) | Update dependencies |
| 0.9.17 | 2026-03-10 | [74601](https://github.com/airbytehq/airbyte/pull/74601) | Update dependencies |
| 0.9.16 | 2026-03-03 | [73562](https://github.com/airbytehq/airbyte/pull/73562) | Update dependencies |
| 0.9.15 | 2026-02-03 | [72578](https://github.com/airbytehq/airbyte/pull/72578) | Update dependencies |
| 0.9.14 | 2026-01-20 | [72096](https://github.com/airbytehq/airbyte/pull/72096) | Update dependencies |
| 0.9.13 | 2026-01-14 | [71517](https://github.com/airbytehq/airbyte/pull/71517) | Update dependencies |
| 0.9.12 | 2025-12-18 | [70669](https://github.com/airbytehq/airbyte/pull/70669) | Update dependencies |
| 0.9.11 | 2025-11-25 | [70115](https://github.com/airbytehq/airbyte/pull/70115) | Update dependencies |
| 0.9.10 | 2025-11-18 | [69655](https://github.com/airbytehq/airbyte/pull/69655) | Update dependencies |
| 0.9.9 | 2025-10-29 | [68882](https://github.com/airbytehq/airbyte/pull/68882) | Update dependencies |
| 0.9.8 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 0.9.7 | 2025-10-21 | [68468](https://github.com/airbytehq/airbyte/pull/68468) | Update dependencies |
| 0.9.6 | 2025-10-14 | [67945](https://github.com/airbytehq/airbyte/pull/67945) | Update dependencies |
| 0.9.5 | 2025-10-07 | [67221](https://github.com/airbytehq/airbyte/pull/67221) | Update dependencies |
| 0.9.4 | 2025-09-30 | [66859](https://github.com/airbytehq/airbyte/pull/66859) | Update dependencies |
| 0.9.3 | 2025-09-24 | [66627](https://github.com/airbytehq/airbyte/pull/66627) | Update dependencies |
| 0.9.2 | 2025-09-09 | [66114](https://github.com/airbytehq/airbyte/pull/66114) | Update dependencies |
| 0.9.1 | 2025-08-24 | [65501](https://github.com/airbytehq/airbyte/pull/65501) | Update dependencies |
| 0.9.0 | 2025-08-21 | [64879](https://github.com/airbytehq/airbyte/pull/64879) | Update events stream to use start and query params instead of filtering on source side |
| 0.8.17 | 2025-08-10 | [64850](https://github.com/airbytehq/airbyte/pull/64850) | Update dependencies |
| 0.8.16 | 2025-08-02 | [64455](https://github.com/airbytehq/airbyte/pull/64455) | Update dependencies |
| 0.8.15 | 2025-07-26 | [63965](https://github.com/airbytehq/airbyte/pull/63965) | Update dependencies |
| 0.8.14 | 2025-07-20 | [63667](https://github.com/airbytehq/airbyte/pull/63667) | Update dependencies |
| 0.8.13 | 2025-07-05 | [62716](https://github.com/airbytehq/airbyte/pull/62716) | Update dependencies |
| 0.8.12 | 2025-06-28 | [61458](https://github.com/airbytehq/airbyte/pull/61458) | Update dependencies |
| 0.8.11 | 2025-05-24 | [60461](https://github.com/airbytehq/airbyte/pull/60461) | Update dependencies |
| 0.8.10 | 2025-05-15 | [60295](https://github.com/airbytehq/airbyte/pull/60295) | Fix missing records for events stream |
| 0.8.9 | 2025-05-10 | [60171](https://github.com/airbytehq/airbyte/pull/60171) | Update dependencies |
| 0.8.8 | 2025-05-04 | [59571](https://github.com/airbytehq/airbyte/pull/59571) | Update dependencies |
| 0.8.7 | 2025-04-27 | [58970](https://github.com/airbytehq/airbyte/pull/58970) | Update dependencies |
| 0.8.6 | 2025-04-19 | [58446](https://github.com/airbytehq/airbyte/pull/58446) | Update dependencies |
| 0.8.5 | 2025-04-12 | [57927](https://github.com/airbytehq/airbyte/pull/57927) | Update dependencies |
| 0.8.4 | 2025-04-05 | [57473](https://github.com/airbytehq/airbyte/pull/57473) | Update dependencies |
| 0.8.3 | 2025-03-29 | [56847](https://github.com/airbytehq/airbyte/pull/56847) | Update dependencies |
| 0.8.2 | 2025-03-22 | [56263](https://github.com/airbytehq/airbyte/pull/56263) | Update dependencies |
| 0.8.1 | 2025-03-08 | [55062](https://github.com/airbytehq/airbyte/pull/55062) | Update dependencies |
| 0.8.0 | 2025-03-05 | [55215](https://github.com/airbytehq/airbyte/pull/55215) | Fix lints for events stream |
| 0.7.0 | 2025-02-25 | [46664](https://github.com/airbytehq/airbyte/pull/46664) | Converting to manifest-only format |
| 0.6.11 | 2025-02-22 | [54521](https://github.com/airbytehq/airbyte/pull/54521) | Update dependencies |
| 0.6.10 | 2025-02-15 | [54100](https://github.com/airbytehq/airbyte/pull/54100) | Update dependencies |
| 0.6.9 | 2025-02-08 | [53513](https://github.com/airbytehq/airbyte/pull/53513) | Update dependencies |
| 0.6.8 | 2025-02-01 | [52979](https://github.com/airbytehq/airbyte/pull/52979) | Update dependencies |
| 0.6.7 | 2025-01-25 | [52503](https://github.com/airbytehq/airbyte/pull/52503) | Update dependencies |
| 0.6.6 | 2025-01-18 | [51896](https://github.com/airbytehq/airbyte/pull/51896) | Update dependencies |
| 0.6.5 | 2025-01-11 | [51335](https://github.com/airbytehq/airbyte/pull/51335) | Update dependencies |
| 0.6.4 | 2025-01-04 | [50930](https://github.com/airbytehq/airbyte/pull/50930) | Update dependencies |
| 0.6.3 | 2024-12-28 | [50709](https://github.com/airbytehq/airbyte/pull/50709) | Update dependencies |
| 0.6.2 | 2024-12-21 | [49058](https://github.com/airbytehq/airbyte/pull/49058) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.6.1 | 2024-11-04 | [43855](https://github.com/airbytehq/airbyte/pull/43855) | Update dependencies |
| 0.6.0 | 2024-10-30 | [47988](https://github.com/airbytehq/airbyte/pull/47988) | Upgrade the CDK and startup files to sync incremental streams concurrently |
| 0.5.3 | 2024-06-06 | [39180](https://github.com/airbytehq/airbyte/pull/39180) | [autopull] Upgrade base image to v1.2.2 |
| 0.5.2 | 2024-05-20 | [38263](https://github.com/airbytehq/airbyte/pull/38263) | Replace AirbyteLogger with logging.Logger |
| 0.5.1 | 2024-04-01 | [36731](https://github.com/airbytehq/airbyte/pull/36731) | Add `%Y-%m-%dT%H:%M:%S%z` to date time formats. |
| 0.5.0 | 2024-03-27 | [35755](https://github.com/airbytehq/airbyte/pull/35755) | Migrate to low-code. |
| 0.4.2 | 2024-03-25 | [36448](https://github.com/airbytehq/airbyte/pull/36448) | Unpin CDK version |
| 0.4.1 | 2024-02-12 | [35145](https://github.com/airbytehq/airbyte/pull/35145) | Manage dependencies with Poetry |
| 0.4.0 | 2024-01-05 | [32957](https://github.com/airbytehq/airbyte/pull/32957) | Added undeclared fields to schema and migrated to base image |
| 0.3.0 | 2023-09-05 | [30192](https://github.com/airbytehq/airbyte/pull/30192) | Added undeclared fields to schema |
| 0.2.4 | 2023-08-14 | [29401](https://github.com/airbytehq/airbyte/pull/29401) | Fix `null` value in stream state |
| 0.2.3 | 2023-08-03 | [29023](https://github.com/airbytehq/airbyte/pull/29023) | Add incremental for `issues` stream |
| 0.2.2 | 2023-05-02 | [25759](https://github.com/airbytehq/airbyte/pull/25759) | Change stream that used in check_connection |
| 0.2.1 | 2023-04-27 | [25602](https://github.com/airbytehq/airbyte/pull/25602) | Add validation of project and organization names during connector setup |
| 0.2.0 | 2023-04-03 | [23923](https://github.com/airbytehq/airbyte/pull/23923) | Add Releases stream |
| 0.1.12 | 2023-03-01 | [23619](https://github.com/airbytehq/airbyte/pull/23619) | Fix bug when `stream state` is `None` or any other bad value occurs |
| 0.1.11 | 2023-02-02 | [22303](https://github.com/airbytehq/airbyte/pull/22303) | Turn ON default AvailabilityStrategy |
| 0.1.10 | 2023-01-27 | [22041](https://github.com/airbytehq/airbyte/pull/22041) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.9 | 2022-12-20 | [21864](https://github.com/airbytehq/airbyte/pull/21864) | Add state persistence to incremental sync |
| 0.1.8 | 2022-12-20 | [20709](https://github.com/airbytehq/airbyte/pull/20709) | Add incremental sync |
| 0.1.7 | 2022-09-30 | [17466](https://github.com/airbytehq/airbyte/pull/17466) | Migrate to per-stream states |
| 0.1.6 | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to the Python CDK |
| 0.1.5 | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime |
| 0.1.4 | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime |
| 0.1.3 | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator |
| 0.1.2 | 2021-12-28 | [15345](https://github.com/airbytehq/airbyte/pull/15345) | Migrate to config-based framework |
| 0.1.1 | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Update fields in source-connectors specifications |
| 0.1.0 | 2021-10-12 | [6975](https://github.com/airbytehq/airbyte/pull/6975) | New Source: Sentry |

</details>
