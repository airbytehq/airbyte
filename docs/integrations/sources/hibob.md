# Hibob

This page contains the setup guide and reference information for the Hibob source connector.

## Prerequisites

- A [HiBob account](https://www.hibob.com) at least
<!-- env:oss -->
- A HiBob Token generated [here](https://apidocs.hibob.com/reference/getting-started-with-bob-api#test-endpoints)
  <!-- /env:oss -->

## Setup guide

<!-- env:oss -->

### Step 1: (For Airbyte Open Source) Setup a HiBob Account

Setup and account in [HiBob](https://www.hibob.com/). 


### Step 2: (For Airbyte Open Source) Obtain an api key

A simple api key is all that is needed to access the HiBob API. This token is generated [here](https://apidocs.hibob.com/docs/api-service-users#step-1-create-a-new-api-service-user).


#### For Airbyte Cloud:

To set up HiBob as a source in Airbyte Cloud:

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **HiBob** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **api key** you obtained from HiBob.
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

To set up HiBob as a source in Airbyte Open Source:

1. Log in to your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **HiBob** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **api key** you obtained from HiBob.
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

## Supported Sync Modes

The HiBob source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

Incremental modes are not supported for the HiBob connector at the time of this writing.

## Supported Streams

The HiBob source connector can sync the following streams.

### Main Tables

Link to HiBob API documentation [here](https://apidocs.hibob.com/docs/).

- [Profiles](https://apidocs.hibob.com/reference/get_profiles)

- [Payroll](https://apidocs.hibob.com/reference/get_payroll-history)


## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request                                             | Subject                                                                                                                              |
|:---------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.7 | 2025-01-11 | [51201](https://github.com/airbytehq/airbyte/pull/51201) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50628](https://github.com/airbytehq/airbyte/pull/50628) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50132](https://github.com/airbytehq/airbyte/pull/50132) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49595](https://github.com/airbytehq/airbyte/pull/49595) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49240](https://github.com/airbytehq/airbyte/pull/49240) | Update dependencies |
| 0.2.2 | 2024-12-11 | [48972](https://github.com/airbytehq/airbyte/pull/48972) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.1 | 2024-10-28 | [47672](https://github.com/airbytehq/airbyte/pull/47672) | Update dependencies |
| 0.2.0 | 2024-08-21 | [44542](https://github.com/airbytehq/airbyte/pull/44542) | Refactor connector to manifest-only format |
| 0.1.3 | 2024-08-17 | [44298](https://github.com/airbytehq/airbyte/pull/44298) | Update dependencies |
| 0.1.2 | 2024-08-12 | [43853](https://github.com/airbytehq/airbyte/pull/43853) | Update dependencies |
| 0.1.1 | 2024-08-10 | [43519](https://github.com/airbytehq/airbyte/pull/43519) | Update dependencies |
| 0.1.0 | 2024-08-06 | [43336](https://github.com/airbytehq/airbyte/pull/43336) | New Source: HiBob |
</details>
