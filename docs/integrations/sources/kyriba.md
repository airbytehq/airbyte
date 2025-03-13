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
| 0.1.36 | 2025-03-08 | [55425](https://github.com/airbytehq/airbyte/pull/55425) | Update dependencies |
| 0.1.35 | 2025-03-01 | [54788](https://github.com/airbytehq/airbyte/pull/54788) | Update dependencies |
| 0.1.34 | 2025-02-22 | [54320](https://github.com/airbytehq/airbyte/pull/54320) | Update dependencies |
| 0.1.33 | 2025-02-15 | [53817](https://github.com/airbytehq/airbyte/pull/53817) | Update dependencies |
| 0.1.32 | 2025-02-01 | [52788](https://github.com/airbytehq/airbyte/pull/52788) | Update dependencies |
| 0.1.31 | 2025-01-25 | [51787](https://github.com/airbytehq/airbyte/pull/51787) | Update dependencies |
| 0.1.30 | 2025-01-11 | [51171](https://github.com/airbytehq/airbyte/pull/51171) | Update dependencies |
| 0.1.29 | 2024-12-28 | [50617](https://github.com/airbytehq/airbyte/pull/50617) | Update dependencies |
| 0.1.28 | 2024-12-21 | [50147](https://github.com/airbytehq/airbyte/pull/50147) | Update dependencies |
| 0.1.27 | 2024-12-14 | [48971](https://github.com/airbytehq/airbyte/pull/48971) | Update dependencies |
| 0.1.26 | 2024-11-25 | [48670](https://github.com/airbytehq/airbyte/pull/48670) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.25 | 2024-11-04 | [48314](https://github.com/airbytehq/airbyte/pull/48314) | Update dependencies |
| 0.1.24 | 2024-10-28 | [47079](https://github.com/airbytehq/airbyte/pull/47079) | Update dependencies |
| 0.1.23 | 2024-10-12 | [46830](https://github.com/airbytehq/airbyte/pull/46830) | Update dependencies |
| 0.1.22 | 2024-10-05 | [46459](https://github.com/airbytehq/airbyte/pull/46459) | Update dependencies |
| 0.1.21 | 2024-09-28 | [46203](https://github.com/airbytehq/airbyte/pull/46203) | Update dependencies |
| 0.1.20 | 2024-09-21 | [45816](https://github.com/airbytehq/airbyte/pull/45816) | Update dependencies |
| 0.1.19 | 2024-09-14 | [45569](https://github.com/airbytehq/airbyte/pull/45569) | Update dependencies |
| 0.1.18 | 2024-09-07 | [45306](https://github.com/airbytehq/airbyte/pull/45306) | Update dependencies |
| 0.1.17 | 2024-08-31 | [45049](https://github.com/airbytehq/airbyte/pull/45049) | Update dependencies |
| 0.1.16 | 2024-08-24 | [44688](https://github.com/airbytehq/airbyte/pull/44688) | Update dependencies |
| 0.1.15 | 2024-08-17 | [44352](https://github.com/airbytehq/airbyte/pull/44352) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43546](https://github.com/airbytehq/airbyte/pull/43546) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43256](https://github.com/airbytehq/airbyte/pull/43256) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42825](https://github.com/airbytehq/airbyte/pull/42825) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42289](https://github.com/airbytehq/airbyte/pull/42289) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41885](https://github.com/airbytehq/airbyte/pull/41885) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41452](https://github.com/airbytehq/airbyte/pull/41452) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41147](https://github.com/airbytehq/airbyte/pull/41147) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40874](https://github.com/airbytehq/airbyte/pull/40874) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40367](https://github.com/airbytehq/airbyte/pull/40367) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40111](https://github.com/airbytehq/airbyte/pull/40111) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39232](https://github.com/airbytehq/airbyte/pull/39232) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-04-19 | [37184](https://github.com/airbytehq/airbyte/pull/37184) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-12 | [37184](https://github.com/airbytehq/airbyte/pull/37184) | schema descriptions |
| 0.1.1 | 2024-01-30 | [34545](https://github.com/airbytehq/airbyte/pull/34545) | Updates CDK, Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.0 | 2022-07-13 | [12748](https://github.com/airbytehq/airbyte/pull/12748) | The Kyriba Source is created |

</details>

</HideInUI>
