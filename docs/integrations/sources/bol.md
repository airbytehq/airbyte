# Bol

[Bol](https://www.bol.com) is the largest online retail platform in the Netherlands and Belgium. This source syncs a seller's data from the [Bol Retailer API v10](https://api.bol.com/retailer/public/redoc/v10/retailer.html): orders, shipments, returns, and inventory.

Maintained by [New North Digital](https://newnorth.nl).

## Prerequisites

- A Bol seller account with access to the Retailer API.
- API credentials (Client ID and Client Secret). Create them in your seller account under **Instellingen → API → Developers / API-credentials**. The connector uses the OAuth 2.0 client-credentials flow against `https://login.bol.com/token`.

## Setup guide

### Step 1: Create Bol API credentials

1. Log in to your Bol seller account.
2. Go to **Instellingen (Settings) → API → API-credentials**.
3. Create a new set of credentials and copy the **Client ID** and **Client Secret**.

### Step 2: Set up the Bol source in Airbyte

1. In the Airbyte UI, click **Sources** and select **Bol**.
2. Enter a **Source name**.
3. Enter your **Client ID** and **Client Secret**.
4. Optionally set a **Start date** (used by the `orders` stream; see Limitations).
5. Click **Set up source**.

## Supported sync modes

The Bol source supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes (`orders` only) |

## Supported Streams

| Stream          | Sync mode          | Primary key  | Notes |
| :-------------- | :----------------- | :----------- | :---- |
| `orders`        | Incremental / Full | `orderId`    | Incremental via Bol's `latest-change-date` filter, one request per day. See Limitations. |
| `orders_fbb`    | Incremental / Full | `orderId`    | FBB/LvB-only subset of `orders` (server-side `fulfilment-method=FBB`). Exists as the parent of `order_details`; usually left unselected. |
| `order_details` | Full Refresh       | `orderId`    | `GET /orders/{orderId}` per changed FBB order. The ONLY stream with money fields: `orderItems[].unitPrice` (incl 21% VAT) and `commission`. See Limitations. |
| `shipments`     | Full Refresh       | `shipmentId` | Snapshot; Bol exposes no change/date filter for shipments. |
| `returns`       | Full Refresh       | `returnId`   | Unions the `handled=false` and `handled=true` partitions. No money fields. |
| `inventory`     | Full Refresh       | `ean`        | LVB/FBB (fulfilment-by-bol) stock snapshot. |

All retailer endpoints are paginated (`?page=N`, 1-indexed) and require the `Accept: application/vnd.retailer.v10+json` header, which the connector sets automatically. The API is rate limited; on HTTP 429 the connector honors Bol's `Retry-After` header (with exponential backoff as fallback).

## Limitations

- **`latest-change-date` is an exact-day filter, not "since".** The API returns orders changed ON the requested day only (verified against the live API; the values are not cumulative). The connector therefore slices the cursor per day (`step P1D`) and issues one request per day between the cursor and now. Treating it as a ">= date" filter silently skips every day except the window start — a bug this connector shipped with until v7.
- **Incremental `orders` is capped to ~3 months.** Bol rejects `latest-change-date` values older than 3 months, so the cursor start is floored at 89 days ago. Orders that have not changed in the last 3 months cannot be retrieved through the Retailer API; this is an API limitation, not a connector one.
- **The order LIST endpoint has no money fields.** `unitPrice` and `commission` only exist on `GET /orders/{orderId}` (the `order_details` stream). Detail calls are rate-limited much harder than the list endpoint: a seller with ~24 orders/day needs ~2,100 detail calls for a full 89-day backfill, which can exceed platform sync timeouts. `order_details` therefore follows the FBB-only parent (`orders_fbb`): for fulfilment-by-bol orders the Retailer API is the only place their revenue exists at all, while merchant-fulfilled (FBR) order revenue is available in the seller's own commerce system.
- **`shipments`, `returns`, and `inventory` are snapshots.** Bol provides no incremental change filter for these endpoints, so each sync re-reads the current state.
- Bol's order list returns a reduced order record; per-item change timestamps are exposed as `orderItems[].latestChangedDateTime`, and the connector derives an order-level `latestChangedDateTime` (the max across items) as the incremental cursor.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
| :------ | :--------- | :----------- | :------ |
| 0.3.0   | 2026-08-05 |              | Fix `latest-change-date` semantics (exact-day filter → daily cursor slices); add `order_details` (prices + commission) behind an FBB-only parent; honor `Retry-After` on 429. |
| 0.1.0   | 2026-06-30 |              | Initial release: orders (incremental), shipments, returns, inventory. |

</details>
