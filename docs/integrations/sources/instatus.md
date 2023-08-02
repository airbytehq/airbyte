# Instatus
This page contains the setup guide and reference information for the Instatus source connector.

## Prerequisites
To set up Metabase you need:
  * `api_key` - Requests to Instatus API must provide an API token.


## Setup guide
### Step 1: Set up Instatus account
### Step 2: Generate an API key
You can get your API key from [User settings](https://dashboard.instatus.com/developer)
Make sure that you are an owner of the pages you want to sync because if you are not this data will be skipped.
### Step 2: Set up the Instatus connector in Airbyte

## Supported sync modes
The Instatus source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)


## Supported Streams
* [Status pages](https://instatus.com/help/api/status-pages)
* [Components](https://instatus.com/help/api/components)
* [Incidents](https://instatus.com/help/api/incidents)
* [Incident updates](https://instatus.com/help/api/incident-updates)
* [Maintenances](https://instatus.com/help/api/maintenances)
* [Maintenance updates](https://instatus.com/help/api/maintenance-updates)
* [Templates](https://instatus.com/help/api/templates)
* [Team](https://instatus.com/help/api/teammates)
* [Subscribers](https://instatus.com/help/api/subscribers)
* [Metrics](https://instatus.com/help/api/metrics)
* [User](https://instatus.com/help/api/user-profile)
* [Public data](https://instatus.com/help/api/public-data)

## Tutorials

### Data type mapping

| Integration Type    | Airbyte Type | Notes |
|:--------------------|:-------------|:------|
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `array`             | `array`      |       |
| `object`            | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
|:------------------|:---------------------|:------|
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |
| Namespaces        | No                   |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------|
| 0.1.0   | 2023-04-01 | [21008](https://github.com/airbytehq/airbyte/pull/21008) | Initial (alpha) release    |