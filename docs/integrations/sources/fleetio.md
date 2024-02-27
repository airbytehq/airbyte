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
| 0.1.0   | 2022-11-02 | [35633](https://github.com/airbytehq/airbyte/pull/35633) | 🎉 New Source: Fleetio source  