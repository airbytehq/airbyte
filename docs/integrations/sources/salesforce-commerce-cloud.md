# Salesforce Commerce Cloud

<HideInUI>

This page contains the setup guide and reference information for the [Salesforce Commerce Cloud](https://developer.salesforce.com/docs/commerce/commerce-api/overview) source connector.

</HideInUI>

## Prerequisites

- A Salesforce Commerce Cloud B2C instance
- An API client configured in [Account Manager](https://account.demandware.com) with appropriate scopes
- Your instance's Organization ID, Short Code, and Site ID

## Setup guide

### Step 1: Obtain API credentials

1. Log in to [Salesforce Commerce Cloud Account Manager](https://account.demandware.com).
2. Navigate to **API Client** and create a new API client or use an existing one.
3. Ensure the client has the following scopes enabled:
   - `sfcc.orders` (for Orders stream)
   - `sfcc.products` (for Products stream)
   - `sfcc.catalogs` (for Catalogs stream)
   - `sfcc.pricing.promotions` (for Promotions stream)
   - `sfcc.pricing.campaigns` (for Campaigns stream)
4. Note the **Client ID** and **Client Secret**.

### Step 2: Find your instance details

- **Organization ID**: Found in Business Manager under **Administration > Site Development > Salesforce Commerce API Settings**. Format: `f_ecom_xxxx_prd`.
- **Short Code**: Found in the same location. Used in the API base URL.
- **Site ID**: The identifier for your storefront site (for example, `SiteGenesis` or `RefArch`).

### Step 3: Set up the connector in Airbyte

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Salesforce Commerce Cloud** from the Source type dropdown.
4. Enter your **Client ID** and **Client Secret**.
5. Enter your **Organization ID**, **Short Code**, and **Site ID**.
6. Optionally set a **Start Date** for incremental sync (defaults to 2020-01-01).
7. Click **Set up source**.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Salesforce Commerce Cloud source connector supports the following [sync modes](https://docs.airbyte.com/using-airbyte/core-concepts/sync-modes/):

| Feature                        | Supported? |
| :----------------------------- | :--------- |
| Full Refresh Overwrite         | Yes        |
| Full Refresh Append            | Yes        |
| Incremental Append             | Yes        |
| Incremental Append + Deduped   | Yes        |

## Supported streams

| Stream | API Endpoint | Sync Mode | Primary Key |
| :--- | :--- | :--- | :--- |
| [Orders](https://developer.salesforce.com/docs/commerce/commerce-api/references/orders?meta=getOrders) | GET /checkout/orders/v1/.../orders | Incremental | orderNo |
| Catalogs | GET /product/catalogs/v1/.../catalogs | Full Refresh | id |
| Categories | `GET /product/catalogs/v1/.../catalogs/{catalogId}/categories` | Full Refresh | id |
| Products | `POST /product/catalogs/v1/.../categories/{categoryId}/products` | Full Refresh | id |
| Promotions | POST /pricing/promotions/v1/.../promotions | Full Refresh | id |
| Campaigns | POST /pricing/campaigns/v1/.../campaigns | Full Refresh | id |

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Salesforce Commerce Cloud connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Salesforce Commerce Cloud APIs use throttle windows of 5-60 seconds. The connector does not currently implement automatic retry on rate limit responses. If you encounter rate limiting, consider reducing sync frequency.

#### Products stream

The SCAPI Admin Products API only exposes single-product endpoints (by product ID). The connector works around this by using a SubstreamPartitionRouter chain: Catalogs → Categories → Products. This means products are discovered by iterating through each catalog's categories and searching for products assigned to each category.

#### Offset pagination limit

The Orders API caps offset + limit at 10,000. For large datasets, incremental sync with date windowing mitigates this limitation.

### Troubleshooting

- Check out common troubleshooting issues for the Salesforce Commerce Cloud source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                        |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------- |
| 0.1.0   | 2026-02-13 | [73343](https://github.com/airbytehq/airbyte/pull/73343)  | Initial release with Orders, Catalogs, Categories, Products, Promotions, and Campaigns streams |

</details>

</HideInUI>
