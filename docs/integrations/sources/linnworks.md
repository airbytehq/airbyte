# Linnworks

This page contains the setup guide and reference information for the [Linnworks](https://www.linnworks.com) source connector.

## Prerequisites

- A Linnworks account

## Setup guide

### Generate Credentials in Linnworks

1. The Linnworks platform has two portals: Seller and Developer. To generate the necessary credentials, log in to the [developer portal](https://developer.linnworks.com) and select **+ New App**.
2. Input a name for your application and set the **Application Type** to `System Integration`.
3. Select **Edit** for your new application. In the **General** tab, find and copy your **Application ID** and **Application Secret**. Click on the **Installation URL** to complete the installation of your app and acquire your **API Token**.

:::tip
The value of your API Token can be viewed at any time from the main dashboard of your account, listed in your app's **Installs** table.
:::

### Set up the connector in Airbyte

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. From the Airbyte UI, click **Sources** > **+ New Source**.
3. Select **Linnworks** from the list of available sources.
4. Enter a **Name** of your choosing.
5. Enter your **Application ID**, **Application Secret** and **API Token**.
6. Enter a **Start date** using the provided datepicker. When using Incremental sync mode, only data generated after this date will be fetched.
7. Select **Set up source** and wait for the connection test to complete.

## Supported streams and sync modes

The Linnworks source connector supports the following streams and [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

| Stream Name                                                                                    | Full Refresh | Incremental |
| :--------------------------------------------------------------------------------------------- | :----------- | :---------- |
| [ProcessedOrders](https://apps.linnworks.net/Api/Method/ProcessedOrders-SearchProcessedOrders) | ✓            | ✓           |
| [ProcessedOrderDetails](https://apps.linnworks.net/Api/Method/Orders-GetOrdersById)            | ✓            | ✓           |
| [StockItems](https://apps.linnworks.net//Api/Method/Stock-GetStockItemsFull)                   | ✓            | X           |
| [StockLocations](https://apps.linnworks.net/Api/Method/Inventory-GetStockLocations)            | ✓            | X           |
| [StockLocationDetails](https://apps.linnworks.net/Api/Method/Locations-GetLocation)            | ✓            | X           |

### Data type mapping

| Integration Type | Airbyte Type | Example              |
| :--------------- | :----------- | :------------------- |
| `number`         | `number`     | 50.23                |
| `integer`        | `integer`    | 50                   |
| `date`           | `string`     | 2020-12-31           |
| `datetime`       | `string`     | 2020-12-31T07:30:00  |
| `array`          | `array`      | ["Item 1", "Item 2"] |
| `boolean`        | `boolean`    | True/False           |
| `string`         | `string`     | Item 3               |

## Limitations & Troubleshooting

<details>
<summary>

Expand to see details about Linnworks connector limitations and troubleshooting

</summary>

### Rate limits

Rate limits for the Linnworks API vary across endpoints. Use the [links in the **Supported Streams** table](#supported-streams-and-sync-modes) to view each endpoint's limits. Rate limited requests will receive a 429 response, but the Linnworks connector should not run into Linnworks API limitations under normal usage.

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------- |
| 0.1.30 | 2024-10-12 | [46798](https://github.com/airbytehq/airbyte/pull/46798) | Update dependencies |
| 0.1.29 | 2024-10-05 | [46406](https://github.com/airbytehq/airbyte/pull/46406) | Update dependencies |
| 0.1.28 | 2024-09-28 | [46124](https://github.com/airbytehq/airbyte/pull/46124) | Update dependencies |
| 0.1.27 | 2024-09-21 | [45730](https://github.com/airbytehq/airbyte/pull/45730) | Update dependencies |
| 0.1.26 | 2024-09-14 | [45571](https://github.com/airbytehq/airbyte/pull/45571) | Update dependencies |
| 0.1.25 | 2024-09-07 | [45262](https://github.com/airbytehq/airbyte/pull/45262) | Update dependencies |
| 0.1.24 | 2024-08-31 | [44968](https://github.com/airbytehq/airbyte/pull/44968) | Update dependencies |
| 0.1.23 | 2024-08-24 | [44740](https://github.com/airbytehq/airbyte/pull/44740) | Update dependencies |
| 0.1.22 | 2024-08-17 | [44304](https://github.com/airbytehq/airbyte/pull/44304) | Update dependencies |
| 0.1.21 | 2024-08-10 | [43604](https://github.com/airbytehq/airbyte/pull/43604) | Update dependencies |
| 0.1.20 | 2024-08-03 | [43183](https://github.com/airbytehq/airbyte/pull/43183) | Update dependencies |
| 0.1.19 | 2024-07-27 | [42608](https://github.com/airbytehq/airbyte/pull/42608) | Update dependencies |
| 0.1.18 | 2024-07-20 | [42235](https://github.com/airbytehq/airbyte/pull/42235) | Update dependencies |
| 0.1.17 | 2024-07-13 | [41778](https://github.com/airbytehq/airbyte/pull/41778) | Update dependencies |
| 0.1.16 | 2024-07-10 | [41432](https://github.com/airbytehq/airbyte/pull/41432) | Update dependencies |
| 0.1.15 | 2024-07-09 | [41219](https://github.com/airbytehq/airbyte/pull/41219) | Update dependencies |
| 0.1.14 | 2024-07-06 | [40870](https://github.com/airbytehq/airbyte/pull/40870) | Update dependencies |
| 0.1.13 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.12 | 2024-06-25 | [40275](https://github.com/airbytehq/airbyte/pull/40275) | Update dependencies |
| 0.1.11 | 2024-06-22 | [40146](https://github.com/airbytehq/airbyte/pull/40146) | Update dependencies |
| 0.1.10 | 2024-06-06 | [39196](https://github.com/airbytehq/airbyte/pull/39196) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.9 | 2024-04-19 | [37188](https://github.com/airbytehq/airbyte/pull/37188) | Updating to 0.80.0 CDK |
| 0.1.8 | 2024-04-12 | [37188](https://github.com/airbytehq/airbyte/pull/37188) | schema descriptions |
| 0.1.7 | 2024-02-22 | [35557](https://github.com/airbytehq/airbyte/pull/35557) | Manage dependencies with Poetry |
| 0.1.6 | 2024-01-31 | [34717](https://github.com/airbytehq/airbyte/pull/34717) | Update CDK and migrate to base image |
| 0.1.5 | 2022-11-20 | [19865](https://github.com/airbytehq/airbyte/pull/19865) | Bump Version |
| 0.1.4 | 2021-11-24 | [8226](https://github.com/airbytehq/airbyte/pull/8226) | Source Linnworks: improve streams ProcessedOrders and ProcessedOrderDetails |
| 0.1.3 | 2021-11-24 | [8169](https://github.com/airbytehq/airbyte/pull/8169) | Source Linnworks: refactor stream StockLocations |
| 0.1.2 | 2021-11-23 | [8177](https://github.com/airbytehq/airbyte/pull/8177) | Source Linnworks: add stream ProcessedOrderDetails |
| 0.1.0 | 2021-11-09 | [7588](https://github.com/airbytehq/airbyte/pull/7588) | New Source: Linnworks |

</details>
