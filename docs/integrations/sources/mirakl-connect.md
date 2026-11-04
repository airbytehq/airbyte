# Mirakl Connect

This page contains the setup guide and reference information for the [Mirakl Connect](https://www.mirakl.com/products/mirakl-connect) source connector.

Mirakl Connect is the seller-side channel platform from Mirakl: one account and one API for the orders, returns, catalog and customer conversations of every marketplace and sales channel a seller works with. This connector reads that data from the [Mirakl Connect APIs](https://developer.mirakl.com/content/product/connect/rest/connect/openapi3).

This connector is for sellers who use Mirakl Connect. It does not read the operator or shop APIs of an individual Mirakl-powered marketplace (`https://<marketplace>.mirakl.net/api`).

## Prerequisites

- A Mirakl Connect company account.
- OAuth2 API credentials (a client ID and a client secret) for your company, created in Mirakl Connect as described in Mirakl's "Integrating with Connect APIs" help article. The client secret is only shown once. The credentials need the scopes of the streams you want to sync.

## Setup guide

### Step 1: Create API credentials in Mirakl Connect

1. In Mirakl Connect, create API credentials for your company.
2. Copy the **client ID** and the **client secret**.

The connector exchanges them for a short-lived access token at the Mirakl Authentication System (`https://auth.mirakl.net/oauth/token`, client credentials grant) and renews the token when it expires.

### Step 2: Set up the Mirakl Connect connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Mirakl Connect** from the Source type dropdown.
4. Enter a name for the Mirakl Connect connector.
5. Enter the **Client ID** and the **Client secret**.
6. (Optional) Enter a **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format. On the first sync, incremental streams only read records updated after this time. The default is `2020-01-01T00:00:00Z`.
7. Click **Set up source**.

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Mirakl Connect** from the Source type dropdown.
4. Enter a name for the Mirakl Connect connector.
5. Fill in the fields as described for Airbyte Cloud above.
6. Click **Set up source**.

## Supported sync modes

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

| Stream          | Endpoint                   | Primary key | Sync modes                |
| :-------------- | :------------------------- | :---------- | :------------------------ |
| orders          | `GET /v2/orders`           | id          | Full Refresh, Incremental |
| returns         | `GET /v2/orders/returns`   | id          | Full Refresh, Incremental |
| order_documents | `GET /v2/orders/documents` | id          | Full Refresh, Incremental |
| conversations   | `GET /conversations`       | id          | Full Refresh, Incremental |
| products        | `GET /products`            | id          | Full Refresh              |

### Incremental streams

Incremental streams use the `updated_at` field as the cursor and pass the saved state to the API's `updated_from` filter. The filter is sent with second precision and includes the boundary, so records updated within the same second as the saved cursor can be read again. Append + Deduped sync mode removes those duplicates.

The `updated_from` filter is always sent on the first page, also in full refresh mode, because the orders endpoint otherwise only returns the last 30 days. Mirakl Connect uses seek pagination: the `next_page_token` returned by the API already contains the original filters, so follow-up pages only send `page_token` and `limit`.

`order_documents` contains document metadata (type, name, size, order ID). The documents themselves are not downloaded.

## Limitations and performance considerations

Mirakl recommends calling the order and return endpoints at most once per minute. The connector requests 100 records per page (1,000 for products), runs at most 2 streams at a time, and retries HTTP 429 and 5xx responses with exponential backoff.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                     | Subject                    |
| :------ | :--------- | :--------------------------------------------------------------- | :------------------------- |
| 0.1.0   | 2026-11-04 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | New Source: Mirakl Connect |

</details>
