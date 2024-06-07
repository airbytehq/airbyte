# Sentry

This page contains the setup guide and reference information for the Sentry source connector.

## Prerequisites

To set up the Sentry source connector, you'll need the Sentry [project name](https://docs.sentry.io/product/projects/), [authentication token](https://docs.sentry.io/api/auth/#auth-tokens), and [organization](https://docs.sentry.io/product/accounts/membership/).

## Set up the Sentry connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Sentry** from the Source type dropdown.
4. Enter the name for the Sentry connector.
5. For **Project**, enter the name of the [Sentry project](https://docs.sentry.io/product/projects/) you want to sync.
6. For **Host Name**, enter the host name of your self-hosted Sentry API Server. If your server isn't self-hosted, leave the field blank.
7. For **Authentication Tokens**, enter the [Sentry authentication token](https://docs.sentry.io/api/auth/#auth-tokens).
8. For **Organization**, enter the [Sentry Organization](https://docs.sentry.io/product/accounts/membership/) the groups belong to.
9. Click **Set up source**.

## Supported sync modes

The Sentry source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Events](https://docs.sentry.io/api/events/list-a-projects-error-events/)
- [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/)
- [Projects](https://docs.sentry.io/api/projects/list-your-projects/)
- [Releases](https://docs.sentry.io/api/releases/list-an-organizations-releases/)

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Sentry connector limitations and troubleshooting.
</summary>

### Connector limitations

:::warning
**Sentry API Restriction on Events Data**: Access to the events endpoint is guaranteed only for the last 90 days by Sentry. If you use the Full Refresh Overwrite sync, be aware that any events data older than 90 days will be **deleted** from your target destination and replaced with the data from the last 90 days only. Use an Append sync mode to ensure historical data is retained.
Please be aware: this also means that any change older than 90 days will not be replicated using the incremental sync mode. If you want all your synced data to remain up to date, please set up your sync frequency to no more than 90 days.
:::

</details>

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |

## Changelog
<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------- |
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
