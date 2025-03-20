# Fleetio API

The Fleetio API Documentation can be found [here](https://developer.fleetio.com)

## Sync Overview

This connector works with the Fleetio API. The connector currently support Full Table Refreshes only.

### Output schema

The output schemas are:

- [contacts](https://developer.fleetio.com/docs/api/v-2-contacts-index)
- [expense_entries](https://developer.fleetio.com/docs/api/v-1-expense-entries-index)
- [fuel_entries](https://developer.fleetio.com/docs/api/v-1-fuel-entries-index)
- [issues](https://developer.fleetio.com/docs/api/v-2-issues-index)
- [parts](https://developer.fleetio.com/docs/api/v-1-parts-index)
- [purchase_orders](https://developer.fleetio.com/docs/api/v-1-purchase-orders-index)
- [service_entries](https://developer.fleetio.com/docs/api/v-2-service-entries-index)
- [submitted_inspection_forms](https://developer.fleetio.com/docs/api/v-1-submitted-inspection-forms-index)
- [vehicle_assignments](https://developer.fleetio.com/docs/api/v-1-vehicle-assignments-index)
- [vehicles](https://developer.fleetio.com/docs/api/v-1-vehicles-index)

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Our source connector adheres to the standard rate limiting with the Airbyte low-code CDK. More information on Fleetio API rate limiting can be found [here](https://developer.fleetio.com/docs/overview/rate-limiting).

## Getting started

### Requirements

- An active Fleetio account
- A Fleetio `api_key` and `account_token`

### Setup guide:

1. Generate your Fleetio API Credentials, which is described [here](https://developer.fleetio.com/docs/overview/quick-start).
2. In the left navigation bar, click **Sources**. in the top-right corner, click **New Source**
3. Set the name for your source
4. Authenticate using the credentials generated in step 1.
5. Click **Set up source**

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.2.15 | 2025-03-08 | [54935](https://github.com/airbytehq/airbyte/pull/54935) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54420](https://github.com/airbytehq/airbyte/pull/54420) | Update dependencies |
| 0.2.13 | 2025-02-15 | [53763](https://github.com/airbytehq/airbyte/pull/53763) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53363](https://github.com/airbytehq/airbyte/pull/53363) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52868](https://github.com/airbytehq/airbyte/pull/52868) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52316](https://github.com/airbytehq/airbyte/pull/52316) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51679](https://github.com/airbytehq/airbyte/pull/51679) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51133](https://github.com/airbytehq/airbyte/pull/51133) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50576](https://github.com/airbytehq/airbyte/pull/50576) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50053](https://github.com/airbytehq/airbyte/pull/50053) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49495](https://github.com/airbytehq/airbyte/pull/49495) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49162](https://github.com/airbytehq/airbyte/pull/49162) | Update dependencies |
| 0.2.3 | 2024-12-11 | [48943](https://github.com/airbytehq/airbyte/pull/48943) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-11-04 | [48145](https://github.com/airbytehq/airbyte/pull/48145) | Update dependencies |
| 0.2.1 | 2024-10-29 | [47932](https://github.com/airbytehq/airbyte/pull/47932) | Update dependencies |
| 0.2.0 | 2024-08-22 | [44567](https://github.com/airbytehq/airbyte/pull/44567) | Refactor connector to manifest-only format |
| 0.1.11 | 2024-08-17 | [44268](https://github.com/airbytehq/airbyte/pull/44268) | Update dependencies |
| 0.1.10 | 2024-08-12 | [43927](https://github.com/airbytehq/airbyte/pull/43927) | Update dependencies |
| 0.1.9 | 2024-08-10 | [43534](https://github.com/airbytehq/airbyte/pull/43534) | Update dependencies |
| 0.1.8 | 2024-08-03 | [43103](https://github.com/airbytehq/airbyte/pull/43103) | Update dependencies |
| 0.1.7 | 2024-07-27 | [42695](https://github.com/airbytehq/airbyte/pull/42695) | Update dependencies |
| 0.1.6 | 2024-07-20 | [42383](https://github.com/airbytehq/airbyte/pull/42383) | Update dependencies |
| 0.1.5 | 2024-07-13 | [41717](https://github.com/airbytehq/airbyte/pull/41717) | Update dependencies |
| 0.1.4 | 2024-07-10 | [41476](https://github.com/airbytehq/airbyte/pull/41476) | Update dependencies |
| 0.1.3 | 2024-07-09 | [41299](https://github.com/airbytehq/airbyte/pull/41299) | Update dependencies |
| 0.1.2 | 2024-07-06 | [39964](https://github.com/airbytehq/airbyte/pull/39964) | Update dependencies |
| 0.1.1   | 2024-07-02 | [40695](https://github.com/airbytehq/airbyte/pull/40695) | upgrade to base image 1.2.2 and metadata fixes
| 0.1.0   | 2022-11-02 | [35633](https://github.com/airbytehq/airbyte/pull/35633) | 🎉 New Source: Fleetio source
