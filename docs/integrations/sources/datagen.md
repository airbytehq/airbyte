# DataGen

The DataGen source connector generates synthetic data for testing and development purposes. This connector is designed for end-to-end testing of data destinations and for testing Airbyte configurations in speed mode without requiring access to an external data source.

## Prerequisites

No prerequisites are required to use this connector. DataGen generates data locally and does not connect to any external systems.

## Setup guide

1. Log in to your Airbyte Cloud or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **DataGen** from the Source type dropdown.
4. Enter a name for your DataGen source.
5. Configure the data generation settings:
   - **Data Generation Type**: Choose either **Incremental** or **All Types**.
   - **Max Record**: Specify the total number of records to generate (minimum 1, maximum 100 billion). Default is 100.
   - **Max Concurrency** (optional): Set the maximum number of concurrent data generators. Leave empty to let Airbyte optimize performance automatically.
6. Click **Set up source**.

## Supported sync modes

The DataGen source connector supports the following sync mode:

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported data generation types

The connector supports two data generation patterns:

### Incremental

Generates a stream named `increment` with a single column named `id` that contains monotonically increasing integers. This mode is useful for testing incremental data loading and verifying that data arrives in the expected order.

### All types

Generates a stream named `all types` with columns for various Airbyte data types, including id, string, boolean, number, big integer, big decimal, date, time (with and without time zones), timestamp (with and without time zones), and JSON. This mode is useful for testing type handling and schema compatibility across different destinations.

## Changelog

<details>
    <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------|
| 0.1.6   | 2025-10-23 | [68611](https://github.com/airbytehq/airbyte/pull/68611) | Update cdk version                 |
| 0.1.5   | 2025-10-21 | [68581](https://github.com/airbytehq/airbyte/pull/68581) | Update dataChannel version         |
| 0.1.4   | 2025-10-15 | [68131](https://github.com/airbytehq/airbyte/pull/68131) | Increment naming fix               |
| 0.1.3   | 2025-10-15 | [68129](https://github.com/airbytehq/airbyte/pull/68129) | Increment encoding fix             |
| 0.1.2   | 2025-10-13 | [67720](https://github.com/airbytehq/airbyte/pull/67720) | Removal of Array type              |
| 0.1.1   | 2025-10-08 | [67110](https://github.com/airbytehq/airbyte/pull/67110) | Addition of proto types            |
| 0.1.0   | 2025-09-16 | [66331](https://github.com/airbytehq/airbyte/pull/66331) | Creation of initial DataGen Source |
</details>
