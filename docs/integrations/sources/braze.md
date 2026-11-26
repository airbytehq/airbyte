# Braze

This page contains the setup guide and reference information for the Braze source connector.

## Prerequisites

It is required to have an account on Braze to provide us with `URL` and `Rest API Key` during set up.

- `Rest API Key` could be found on Braze Dashboard -> Developer Console tab -> API Settings -> Rest API Keys
- `URL` could be found on Braze Dashboard -> Manage Settings -> Settings tab -> `Your App name` -> SDK Endpoint

## Set up the Braze connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Braze connector and select **Braze** from the Source type dropdown.
4. Fill in your `URL`, `Rest API Key` and `Start date` and then click **Set up source**.

## Supported sync modes

The Braze source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh | Overwrite
- Incremental Sync | Append

## Supported Streams

- [campaigns](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaigns) — supports incremental sync.
- [campaigns_analytics](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaign_analytics)
- [campaigns_details](https://www.braze.com/docs/api/endpoints/export/campaigns/get_campaign_details)
- [canvases](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas) — supports incremental sync.
- [canvases_analytics](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_analytics)
- [canvases_details](https://www.braze.com/docs/api/endpoints/export/canvas/get_canvas_details)
- [events](https://www.braze.com/docs/api/endpoints/export/custom_events/get_custom_events)
- [events_analytics](https://www.braze.com/docs/api/endpoints/export/custom_events/get_custom_events_analytics)
- [kpi_daily_new_users](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_daily_new_users)
- [kpi_daily_active_users](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_daily_active_users)
- [kpi_daily_app_uninstalls](https://www.braze.com/docs/api/endpoints/export/kpi/get_kpi_daily_app_uninstalls)
- cards — Braze retired News Feed; this stream returns no records.
- cards_analytics — Braze retired News Feed; this stream returns no records.
- [segments](https://www.braze.com/docs/api/endpoints/export/segments/get_segment)
- [segments_analytics](https://www.braze.com/docs/api/endpoints/export/segments/get_segment_analytics)
- [segments_details](https://www.braze.com/docs/api/endpoints/export/segments/get_segment_details)

## Performance considerations

Rate limits differ depending on stream.

Rate limits table: https://www.braze.com/docs/api/api_limits/#rate-limits-by-request-type

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                            |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------- |
| 0.5.0 | 2026-11-16 | [93036](https://github.com/airbytehq/airbyte/pull/93036) | Upgrade to source-declarative-manifest 7.47.0, add incremental sync for campaigns and canvases, include archived campaigns and canvases, fix pagination page sizes, and complete retired News Feed streams without failing the sync |
| 0.4.20 | 2025-08-16 | [65057](https://github.com/airbytehq/airbyte/pull/65057) | Update dependencies |
| 0.4.19 | 2025-08-02 | [64411](https://github.com/airbytehq/airbyte/pull/64411) | Update dependencies |
| 0.4.18 | 2025-07-26 | [63796](https://github.com/airbytehq/airbyte/pull/63796) | Update dependencies |
| 0.4.17 | 2025-07-08 | [62858](https://github.com/airbytehq/airbyte/pull/62858) | Updated Schema for `campaigns_details`, `campaigns_analytics`, and `campaigns` |
| 0.4.16 | 2025-07-05 | [62528](https://github.com/airbytehq/airbyte/pull/62528) | Update dependencies |
| 0.4.15 | 2025-06-28 | [60648](https://github.com/airbytehq/airbyte/pull/60648) | Update dependencies |
| 0.4.14 | 2025-05-10 | [59854](https://github.com/airbytehq/airbyte/pull/59854) | Update dependencies |
| 0.4.13 | 2025-05-03 | [59309](https://github.com/airbytehq/airbyte/pull/59309) | Update dependencies |
| 0.4.12 | 2025-04-26 | [58732](https://github.com/airbytehq/airbyte/pull/58732) | Update dependencies |
| 0.4.11 | 2025-04-19 | [58230](https://github.com/airbytehq/airbyte/pull/58230) | Update dependencies |
| 0.4.10 | 2025-04-12 | [57643](https://github.com/airbytehq/airbyte/pull/57643) | Update dependencies |
| 0.4.9 | 2025-04-05 | [57132](https://github.com/airbytehq/airbyte/pull/57132) | Update dependencies |
| 0.4.8 | 2025-03-29 | [56574](https://github.com/airbytehq/airbyte/pull/56574) | Update dependencies |
| 0.4.7 | 2025-03-22 | [56122](https://github.com/airbytehq/airbyte/pull/56122) | Update dependencies |
| 0.4.6 | 2025-03-08 | [55410](https://github.com/airbytehq/airbyte/pull/55410) | Update dependencies |
| 0.4.5 | 2025-03-01 | [54858](https://github.com/airbytehq/airbyte/pull/54858) | Update dependencies |
| 0.4.4 | 2025-02-22 | [54275](https://github.com/airbytehq/airbyte/pull/54275) | Update dependencies |
| 0.4.3 | 2025-02-15 | [53870](https://github.com/airbytehq/airbyte/pull/53870) | Update dependencies |
| 0.4.2 | 2025-02-08 | [53426](https://github.com/airbytehq/airbyte/pull/53426) | Update dependencies |
| 0.4.1 | 2025-02-01 | [52922](https://github.com/airbytehq/airbyte/pull/52922) | Update dependencies |
| 0.4.0 | 2024-10-24 | [47329](https://github.com/airbytehq/airbyte/pull/47329) | Migrate to Manifest-only |
| 0.3.0 | 2023-11-04 | [31857](https://github.com/airbytehq/airbyte/pull/31857) | Add Campaigns, Canvases, Segments Details Streams |
| 0.2.0 | 2023-10-28 | [31607](https://github.com/airbytehq/airbyte/pull/31607) | Fix CanvasAnalytics Stream Null Data for step_stats, variant_stats |
| 0.1.4 | 2023-11-03 | [20520](https://github.com/airbytehq/airbyte/pull/20520) | Fix integration tests |
| 0.1.3 | 2022-12-15 | [20520](https://github.com/airbytehq/airbyte/pull/20520) | The Braze connector born |

</details>
