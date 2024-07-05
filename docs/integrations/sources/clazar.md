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

| Feature                      | Supported? |
|:-----------------------------|:-----------|
| Full Refresh Overwrite       | Yes        |
| Full Refresh Append          | Yes        |
| Incremental Append           | No         |
| Incremental Append + Deduped | No         |

## Supported Streams


- [Listings](https://developers.clazar.io/reference/get-listings)
- [Private Offers](https://developers.clazar.io/reference/get-private-offers)
- [Buyers](https://developers.clazar.io/reference/get-buyers)
- [Contracts](https://developers.clazar.io/reference/get-contracts-1)
- Opportunities
- Analytics
  - AWS
    - Disbursement
    - Revenue
    - Opportunities
  - Azure
    - Revenue
    - Customers
    - Orders
    - Metered usage
    - Opportunities
  - GCP
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

| Version | Date       | Pull Request                                             | Subject            |
|:--------|:-----------|:---------------------------------------------------------|:-------------------|
| 0.1.0   | 2024-06-27 | [40562](https://github.com/airbytehq/airbyte/pull/40562) | New Source: Clazar |

</details>

</HideInUI>
