# SurveyCTO

This page guides you through setting up the [SurveyCTO](https://www.surveycto.com/) source connector. The connector exports form submissions from your SurveyCTO server using the SurveyCTO REST API.

:::note
This connector is available in Airbyte Open Source only. It isn't available in Airbyte Cloud.
:::

## Prerequisites

- A SurveyCTO server. The server name is the subdomain of your server URL. For example, if you access your server at `https://example.surveycto.com`, the server name is `example`.
- A SurveyCTO user whose role has API access enabled. SurveyCTO enables or disables API access per role. See [Managing user roles](https://docs.surveycto.com/04-monitoring-and-management/01-the-basics/00b.managing-user-roles.html) and [Accessing server data via an API](https://docs.surveycto.com/05-exporting-and-publishing-data/05-api-access/01.api-access.html). API access also depends on your SurveyCTO subscription plan.
- The username and password for that user. The connector authenticates with HTTP basic authentication.
- The form ID of each deployed form you want to sync.

## Set up the SurveyCTO source connector

1. In Airbyte, click **Sources**, then click **+ New source**.
2. Select **SurveyCTO** from the list of sources.
3. Enter a name for your source.
4. For **Server Name**, enter the name of your SurveyCTO server, without `.surveycto.com`.
5. For **Username** and **Password**, enter the credentials of the SurveyCTO user with API access.
6. For **Form Id's**, enter the ID of each form you want to sync. You can add more than one form ID.
7. (Optional) For **Start Date**, enter the date from which to export submissions, in the format `Mon DD, YYYY HH:MM:SS AM`, for example `Jan 09, 2022 00:00:00 AM`. If you don't set a value, the connector uses `Jan 09, 2022 00:00:00 AM`.
8. Click **Set up source**.

When you set up the source, the connector checks the connection by requesting submissions for each form ID. If any form ID is invalid or the user lacks access, the check fails.

## Supported sync modes

The SurveyCTO source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

## Supported streams

The connector creates one stream for each form ID you configure. Each stream is named after its form ID and contains that form's submissions, exported in SurveyCTO's wide JSON format.

| Primary key | Cursor field     |
| ----------- | ---------------- |
| `KEY`       | `SubmissionDate` |

During incremental syncs, the connector requests only submissions received since the last synced `SubmissionDate`. The first sync starts from the configured **Start Date**.

## Limitations

- The connector infers each stream's schema from the submissions the API returns for that form since the **Start Date**. Fields that don't appear in any of those submissions aren't included in the schema. If a form has no submissions since the **Start Date**, the stream has no fields.
- The connector requests all matching submissions for a form in a single API request, without pagination.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                    |
| ------- | ---------- | -------------------------------------------------------- | -------------------------- |
| 0.1.47 | 2026-11-13 | [89524](https://github.com/airbytehq/airbyte/pull/89524) | Upgrade to airbyte-cdk 7 and Python 3.13 base image; fix connection check failing with urllib3 2.x |
| 0.1.46 | 2025-05-24 | [60563](https://github.com/airbytehq/airbyte/pull/60563) | Update dependencies |
| 0.1.45 | 2025-05-10 | [60167](https://github.com/airbytehq/airbyte/pull/60167) | Update dependencies |
| 0.1.44 | 2025-05-04 | [59619](https://github.com/airbytehq/airbyte/pull/59619) | Update dependencies |
| 0.1.43 | 2025-04-27 | [58447](https://github.com/airbytehq/airbyte/pull/58447) | Update dependencies |
| 0.1.42 | 2025-04-12 | [57425](https://github.com/airbytehq/airbyte/pull/57425) | Update dependencies |
| 0.1.41 | 2025-03-29 | [56881](https://github.com/airbytehq/airbyte/pull/56881) | Update dependencies |
| 0.1.40 | 2025-03-22 | [56267](https://github.com/airbytehq/airbyte/pull/56267) | Update dependencies |
| 0.1.39 | 2025-03-08 | [55571](https://github.com/airbytehq/airbyte/pull/55571) | Update dependencies |
| 0.1.38 | 2025-03-01 | [55135](https://github.com/airbytehq/airbyte/pull/55135) | Update dependencies |
| 0.1.37 | 2025-02-22 | [54459](https://github.com/airbytehq/airbyte/pull/54459) | Update dependencies |
| 0.1.36 | 2025-02-15 | [54099](https://github.com/airbytehq/airbyte/pull/54099) | Update dependencies |
| 0.1.35 | 2025-02-01 | [53098](https://github.com/airbytehq/airbyte/pull/53098) | Update dependencies |
| 0.1.34 | 2025-01-25 | [52427](https://github.com/airbytehq/airbyte/pull/52427) | Update dependencies |
| 0.1.33 | 2025-01-18 | [51958](https://github.com/airbytehq/airbyte/pull/51958) | Update dependencies |
| 0.1.32 | 2025-01-11 | [51455](https://github.com/airbytehq/airbyte/pull/51455) | Update dependencies |
| 0.1.31 | 2024-12-28 | [50804](https://github.com/airbytehq/airbyte/pull/50804) | Update dependencies |
| 0.1.30 | 2024-12-21 | [50303](https://github.com/airbytehq/airbyte/pull/50303) | Update dependencies |
| 0.1.29 | 2024-12-14 | [49765](https://github.com/airbytehq/airbyte/pull/49765) | Update dependencies |
| 0.1.28 | 2024-12-12 | [49385](https://github.com/airbytehq/airbyte/pull/49385) | Update dependencies |
| 0.1.27 | 2024-11-25 | [48658](https://github.com/airbytehq/airbyte/pull/48658) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.26 | 2024-10-29 | [47725](https://github.com/airbytehq/airbyte/pull/47725) | Update dependencies |
| 0.1.25 | 2024-10-28 | [47036](https://github.com/airbytehq/airbyte/pull/47036) | Update dependencies |
| 0.1.24 | 2024-10-12 | [46834](https://github.com/airbytehq/airbyte/pull/46834) | Update dependencies |
| 0.1.23 | 2024-10-05 | [46450](https://github.com/airbytehq/airbyte/pull/46450) | Update dependencies |
| 0.1.22 | 2024-09-28 | [46112](https://github.com/airbytehq/airbyte/pull/46112) | Update dependencies |
| 0.1.21 | 2024-09-21 | [45818](https://github.com/airbytehq/airbyte/pull/45818) | Update dependencies |
| 0.1.20 | 2024-09-14 | [45551](https://github.com/airbytehq/airbyte/pull/45551) | Update dependencies |
| 0.1.19 | 2024-09-07 | [45258](https://github.com/airbytehq/airbyte/pull/45258) | Update dependencies |
| 0.1.18 | 2024-08-31 | [45026](https://github.com/airbytehq/airbyte/pull/45026) | Update dependencies |
| 0.1.17 | 2024-08-24 | [44743](https://github.com/airbytehq/airbyte/pull/44743) | Update dependencies |
| 0.1.16 | 2024-08-17 | [44345](https://github.com/airbytehq/airbyte/pull/44345) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43478](https://github.com/airbytehq/airbyte/pull/43478) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43190](https://github.com/airbytehq/airbyte/pull/43190) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42602](https://github.com/airbytehq/airbyte/pull/42602) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42309](https://github.com/airbytehq/airbyte/pull/42309) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41743](https://github.com/airbytehq/airbyte/pull/41743) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41597](https://github.com/airbytehq/airbyte/pull/41597) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41117](https://github.com/airbytehq/airbyte/pull/41117) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40782](https://github.com/airbytehq/airbyte/pull/40782) | Update dependencies |
| 0.1.7 | 2024-06-26 | [40531](https://github.com/airbytehq/airbyte/pull/40531) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40466](https://github.com/airbytehq/airbyte/pull/40466) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40130](https://github.com/airbytehq/airbyte/pull/40130) | Update dependencies |
| 0.1.4 | 2024-06-04 | [38993](https://github.com/airbytehq/airbyte/pull/38993) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-20 | [38439](https://github.com/airbytehq/airbyte/pull/38439) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-07-27 | [28512](https://github.com/airbytehq/airbyte/pull/28512) | Added Check Connection |
| 0.1.1 | 2023-04-25 | [24784](https://github.com/airbytehq/airbyte/pull/24784) | Fix incremental sync |
| 0.1.0 | 2022-11-16 | [19371](https://github.com/airbytehq/airbyte/pull/19371) | SurveyCTO Source Connector |

</details>
