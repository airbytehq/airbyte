# Kyriba

<HideInUI>

This page contains the setup guide and reference information for the [Kyriba](https://www.kyriba.com/) source connector.

</HideInUI>

## Overview

The Kyriba source retrieves data from [Kyriba](https://kyriba.com/) using their [JSON REST APIs](https://developer.kyriba.com/apiCatalog/).

## Prerequisites

- Kyriba domain
- Username
- Password

## Setup Guide

### Set up the Kyriba source connector in Airbyte

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or your Airbyte Open Source account.
2. Navigate to **Sources** in the left sidebar and click **+ New source**. in the top-right corner.
3. Choose **Kyriba** from the list of available sources.
4. For **Source name**, enter a descriptive name to help you identify this source.
5. For **Domain**, enter your Kyriba domain.
6. Input your **Username** and **Password** for basic authentication.
7. Specify the**Start Date**, from which data syncing will commence.
8. (Optional) Specify an End Date to indicate the last date up to which data will be synced.

<HideInUI>

## Supported Sync Modes

The Kyriba source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

- [Accounts](https://developer.kyriba.com/site/global/apis/accounts/index.gsp)
- [Bank Balances](https://developer.kyriba.com/site/global/apis/bank-statement-balances/index.gsp) - End of Day and Intraday
- [Cash Balances](https://developer.kyriba.com/site/global/apis/cash-balances/index.gsp) - End of Day and Intraday
- [Cash Flows](https://developer.kyriba.com/site/global/apis/cash-flows/index.gsp)

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Kyriba connector limitations and troubleshooting.
</summary>

### Connector Limitations

#### Rate Limiting

The Kyriba connector should not run into API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Troubleshooting

- Check out common troubleshooting issues for the Stripe source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| 0.1.3   | 2024-04-19 | [37184](https://github.com/airbytehq/airbyte/pull/37184) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                                   |
| 0.1.2   | 2024-04-12 | [37184](https://github.com/airbytehq/airbyte/pull/37184) | schema descriptions                                                                          |
| 0.1.1   | 2024-01-30 | [34545](https://github.com/airbytehq/airbyte/pull/34545) | Updates CDK, Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.0   | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created                                                                 |

</details>

</HideInUI>
