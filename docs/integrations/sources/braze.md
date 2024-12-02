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

- [campaigns](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#f3b0b3ef-04fb-4a31-8570-e6ad88dacb18)
- [campaigns_analytics](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#c07b5ebd-0246-471e-b154-416d63ae28a1)
- [canvases](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#e6c150d7-fceb-4b10-91e2-a9ca4d5806d1)
- [canvases_analytics](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#0fd61e93-7edf-4d87-a8dc-052420aefb73)
- [events](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#93ecd8a5-305d-4b72-ae33-2d74983255c1)
- [events_analytics](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#0bd1ab63-d1a5-4301-8d17-246cf24a178c)
- [kpi_daily_new_users](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#07756c39-cfa0-40a0-8101-03f8791cec01)
- [kpi_daily_active_users](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#90a64560-65aa-4f71-a8ef-1edf49321986)
- [kpi_daily_app_uninstalls](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#59c4d592-3e77-42f8-8ff1-d5d250acbeae)
- [cards](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#9fa7a3bc-4a02-4de2-bc4c-8f111750665e)
- [cards_analytics](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#9cdc3b1e-641e-4d62-b9e8-42d04ee9d4d8)
- [segments](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#1349e6f4-3ce7-4e60-b3e9-951c99c0993f)
- [segments_analytics](https://documenter.getpostman.com/view/4689407/SVYrsdsG?version=latest#62d9d142-cdec-4aea-a287-c13efea7415e)

## Performance considerations

Rate limits differ depending on stream.

Rate limits table: https://www.braze.com/docs/api/api_limits/#rate-limits-by-request-type

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                            |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------- |
| 0.3.0   | 2023-11-04 | [31857](https://github.com/airbytehq/airbyte/pull/31857) | Add Campaigns, Canvases, Segments Details Streams                  |
| 0.2.0   | 2023-10-28 | [31607](https://github.com/airbytehq/airbyte/pull/31607) | Fix CanvasAnalytics Stream Null Data for step_stats, variant_stats |
| 0.1.4   | 2023-11-03 | [20520](https://github.com/airbytehq/airbyte/pull/20520) | Fix integration tests                                              |
| 0.1.3   | 2022-12-15 | [20520](https://github.com/airbytehq/airbyte/pull/20520) | The Braze connector born                                           |

</details>