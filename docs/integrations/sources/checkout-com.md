# Checkout.com

This page contains the setup guide and reference information for the [Checkout.com](https://www.checkout.com) source connector.

Checkout.com is a global payments platform. This connector reads payments, payment actions, financial actions (fees and settlement amounts), disputes, reports and workflows from the [Checkout.com API](https://api-reference.checkout.com), so you can reconcile payments and chargebacks in your warehouse.

## Prerequisites

- A Checkout.com account (sandbox or production).
- Either an access key (OAuth client credentials) or a secret API key, created in the Checkout.com Dashboard under **Developers > Keys**.
- The key needs these scopes for the streams you sync: `disputes:view`, `payments:search`, `gateway:payment-details`, `financial-actions:view`, `reports:view` and `flow:workflows`.

## Setup guide

### Step 1: Create credentials in Checkout.com

1. In the [Checkout.com Dashboard](https://dashboard.checkout.com), open **Developers > Keys**.
2. Create an access key (recommended) and note the access key ID (`ack_...`) and secret, or use an existing secret API key (`sk_...`).
3. Give the key the scopes listed above.
4. Note your account's unique base URL prefix from **Developers > Overview** (the part before `.api.checkout.com`). See [API endpoints](https://www.checkout.com/docs/developer-resources/api/api-endpoints).

### Step 2: Set up the Checkout.com connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Checkout.com** from the Source type dropdown.
4. Enter a name for the Checkout.com connector.
5. Choose an **Authentication** method and enter the access key ID and secret, or the secret API key.
6. Set **Environment** to `sandbox` if the credentials were created in the sandbox. The default is `production`.
7. Enter your **Account prefix**. If you leave it empty, the connector uses the global `api.checkout.com` host.
8. (Optional) Enter a **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format. If you leave it empty, the first sync reads the last 90 days.
9. (Optional) Change **Payments search window** or **Payments search query** (see below).
10. Click **Set up source**.

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Checkout.com** from the Source type dropdown.
4. Fill in the fields as described for Airbyte Cloud above.
5. Click **Set up source**.

## Supported sync modes

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

| Stream            | Endpoint                                 | Primary key | Sync modes                |
| :---------------- | :--------------------------------------- | :---------- | :------------------------ |
| disputes          | `GET /disputes`                          | id          | Full Refresh, Incremental |
| payments          | `POST /payments/search`                  | id          | Full Refresh, Incremental |
| payment_actions   | `GET /payments/{id}/actions`             | id          | Full Refresh              |
| financial_actions | `GET /financial-actions?payment_id={id}` | action_id   | Full Refresh              |
| reports           | `GET /reports`                           | id          | Full Refresh, Incremental |
| workflows         | `GET /workflows`                         | id          | Full Refresh              |

### Incremental streams

- `disputes` uses `last_update` as the cursor and the API's `from`/`to` filter.
- `payments` uses `requested_on` and the search API's `from`/`to` range.
- `reports` uses `created_on` and the `created_after`/`created_before` filter.

Checkout.com timestamps have seven fractional digits (for example `2026-01-03T09:00:00.7250000+00:00`). The connector rewrites the cursor field of each record to UTC with microsecond precision (`2026-01-03T09:00:00.725000Z`) so it can be compared; other timestamp fields are left as returned. State is saved with second precision, so a sync can re-read records from the last second of the previous one, and Append + Deduped sync mode removes those duplicates.

### Payments search windows

Checkout.com has no endpoint that lists all payments, so `payments` reads the [payments search API](https://www.checkout.com/docs/payments/manage-payments/search-and-filter-payments) one time window at a time, with up to 1,000 payments per window (60 minutes by default). If a window has more than 1,000 payments, the sync stops with an error asking you to lower **Payments search window** instead of silently skipping payments. **Payments search query** defaults to `amount:>=0`, which matches every payment; you can narrow it, for example to `processing_channel_id:'pc_...'`.

### Payment and financial actions

`payment_actions` and `financial_actions` are read for every payment returned by `payments` in the sync's date range, which costs one or more API calls per payment. They are full refresh only, because actions such as refunds can be added to a payment long after it was requested.

## Limitations and performance considerations

The connector retries HTTP 429 and 5xx responses with exponential backoff. The payments search API documents a default 90-day lookback. Historical backfills of `payment_actions` and `financial_actions` scale with the number of payments, so a narrow start date or search query keeps them fast.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                  |
| :------ | :--------- | :------------------------------------------------------- | :----------------------- |
| 0.1.0   | 2026-11-04 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | New Source: Checkout.com |

</details>
