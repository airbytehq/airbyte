# Clazar

<HideInUI>

This page contains the setup guide and reference information for the [Clazar](https://clazar.io/) source connector.

</HideInUI>

## Prerequisites

- Clazar Account
- Clazar [API Credentials](https://app.clazar.io/settings/api-access)

## Setup Guide

## Step 1: Set up the Clazar connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Generate client credentials by visiting the [API access page](https://app.clazar.io/settings/api-access). 
2. Click on `Create API Credentials` in `Integration Type` select **Airbyte** from dropdown and copy the `Client ID` & `Client secret`. 
3. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
4. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
5. On the Set up the source page, select **Clazar** from the Source type dropdown and enter the name for the Clazar connector
6. Enter your `Client ID` & `Client secret`. 
7. Click **Set up source**

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte OSS:**

1. Generate client credentials by visiting the [API access page](https://app.clazar.io/settings/api-access).
2. Click on `Create API Credentials` in `Integration Type` select **Airbyte** from dropdown and copy the `Client ID` & `Client secret`.
3. Navigate to the Airbyte Open Source dashboard.
4. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
5. On the Set up the source page, select **Clazar** from the Source type dropdown and enter the name for the Clazar connector.
6. Enter your `Client ID` & `Client secret`. 
7. Click **Set up source**

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Clazar source connector supports the following [sync modes](https://docs.airbyte.com/using-airbyte/core-concepts/sync-modes/):

| Feature                      | Supported?                             |
|:-----------------------------|:---------------------------------------|
| Full Refresh Overwrite       | Yes                                    |
| Full Refresh Append          | Yes                                    |
| Incremental Append           | Yes(Partially, some streams supported) |
| Incremental Append + Deduped | Yes(Partially, some streams supported) |

## Supported Streams


- [Listings](https://developers.clazar.io/reference/get-listings)
- [Private Offers](https://developers.clazar.io/reference/get-private-offers)
- [Buyers](https://developers.clazar.io/reference/get-buyers)
- [Contracts](https://developers.clazar.io/reference/get-contracts-1)
- Opportunities
- Analytics
  - [AWS](https://developers.clazar.io/docs/aws-analytics)
    - Disbursement
    - Revenue
    - Opportunities
  - [Azure](https://developers.clazar.io/docs/analytics)
    - Revenue
    - Customers
    - Orders
    - Metered usage
    - Opportunities
  - [GCP](https://developers.clazar.io/docs/gcp-analytics)
    - Disbursement
    - Disbursement summary
    - Charges & usage
    - Daily insights
    - Daily incremental insights
    - Monthly insights
    - Monthly incremental insights

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Clazar connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Clazar Analytics APIs has the rate limits of (30/minute) and for other APIs it's (120/minute), but the connector should not run into API limitations under normal usage.

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Troubleshooting

- Check out common troubleshooting issues for the Clazar source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------|
| 0.4.17 | 2025-03-08 | [55403](https://github.com/airbytehq/airbyte/pull/55403) | Update dependencies |
| 0.4.16 | 2025-03-01 | [54864](https://github.com/airbytehq/airbyte/pull/54864) | Update dependencies |
| 0.4.15 | 2025-02-22 | [54254](https://github.com/airbytehq/airbyte/pull/54254) | Update dependencies |
| 0.4.14 | 2025-02-15 | [53869](https://github.com/airbytehq/airbyte/pull/53869) | Update dependencies |
| 0.4.13 | 2025-02-08 | [53410](https://github.com/airbytehq/airbyte/pull/53410) | Update dependencies |
| 0.4.12 | 2025-02-01 | [52915](https://github.com/airbytehq/airbyte/pull/52915) | Update dependencies |
| 0.4.11 | 2025-01-25 | [52191](https://github.com/airbytehq/airbyte/pull/52191) | Update dependencies |
| 0.4.10 | 2025-01-18 | [51729](https://github.com/airbytehq/airbyte/pull/51729) | Update dependencies |
| 0.4.9 | 2025-01-11 | [51268](https://github.com/airbytehq/airbyte/pull/51268) | Update dependencies |
| 0.4.8 | 2024-12-28 | [50473](https://github.com/airbytehq/airbyte/pull/50473) | Update dependencies |
| 0.4.7 | 2024-12-21 | [50214](https://github.com/airbytehq/airbyte/pull/50214) | Update dependencies |
| 0.4.6 | 2024-12-14 | [49570](https://github.com/airbytehq/airbyte/pull/49570) | Update dependencies |
| 0.4.5 | 2024-12-12 | [49009](https://github.com/airbytehq/airbyte/pull/49009) | Update dependencies |
| 0.4.4 | 2024-11-04 | [48187](https://github.com/airbytehq/airbyte/pull/48187) | Update dependencies |
| 0.4.3 | 2024-10-30 | [46949](https://github.com/airbytehq/airbyte/pull/46949) | Updated the logo |
| 0.4.2 | 2024-10-29 | [47843](https://github.com/airbytehq/airbyte/pull/47843) | Update dependencies |
| 0.4.1 | 2024-10-28 | [47598](https://github.com/airbytehq/airbyte/pull/47598) | Update dependencies |
| 0.4.0 | 2024-08-30 | [44855](https://github.com/airbytehq/airbyte/pull/44855) | Using incremental APIs for online data |
| 0.3.0 | 2024-08-21 | [44523](https://github.com/airbytehq/airbyte/pull/44523) | Refactor connector to manifest-only format |
| 0.2.6 | 2024-08-17 | [44217](https://github.com/airbytehq/airbyte/pull/44217) | Update dependencies |
| 0.2.5 | 2024-08-12 | [43768](https://github.com/airbytehq/airbyte/pull/43768) | Update dependencies |
| 0.2.4 | 2024-08-05 | [42851](https://github.com/airbytehq/airbyte/pull/42851) | Updated schema of Analytics AWS opportunities table |
| 0.2.3 | 2024-08-03 | [43155](https://github.com/airbytehq/airbyte/pull/43155) | Update dependencies |
| 0.2.2 | 2024-07-27 | [42617](https://github.com/airbytehq/airbyte/pull/42617) | Update dependencies |
| 0.2.1 | 2024-07-20 | [42315](https://github.com/airbytehq/airbyte/pull/42315) | Update dependencies |
| 0.2.0 | 2024-07-18 | [41657](https://github.com/airbytehq/airbyte/pull/41657) | removed redundant columns from streams, added documentation for analytics |
| 0.1.4 | 2024-07-13 | [41759](https://github.com/airbytehq/airbyte/pull/41759) | Update dependencies |
| 0.1.3 | 2024-07-10 | [41351](https://github.com/airbytehq/airbyte/pull/41351) | Update dependencies |
| 0.1.2 | 2024-07-09 | [41123](https://github.com/airbytehq/airbyte/pull/41123) | Update dependencies |
| 0.1.1 | 2024-07-06 | [40922](https://github.com/airbytehq/airbyte/pull/40922) | Update dependencies |
| 0.1.0 | 2024-07-02 | [40562](https://github.com/airbytehq/airbyte/pull/40562) | New Source: Clazar |

</details>

</HideInUI>
