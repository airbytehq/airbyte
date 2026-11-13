# Rillet

This page contains the setup guide and reference information for the [Rillet](https://www.rillet.com) source connector.

Rillet is an AI-native ERP and general ledger. This connector reads your chart of accounts, journal entries, accounts receivable (customers, contracts, invoices, payments, credit memos), accounts payable (vendors, bills, vendor credits, charges, reimbursements) and banking data from the [Rillet Accounting API](https://docs.api.rillet.com/docs/getting-started) (API version 4).

## Prerequisites

- A Rillet organization with API access enabled. API access is turned on by your Rillet team.
- A Rillet API key, created in [Organization Settings > API Access](https://app.rillet.io/settings/api-access).

## Setup guide

### Step 1: Create a Rillet API key

1. Ask your Rillet team to enable API access for your organization if it is not enabled yet.
2. In Rillet, open [Organization Settings > API Access](https://app.rillet.io/settings/api-access) and create an API key.
3. Note whether the key belongs to production (`https://api.rillet.com`) or the test environment (`https://sandbox.api.rillet.com`).

### Step 2: Set up the Rillet connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Rillet** from the Source type dropdown.
4. Enter a name for the Rillet connector.
5. Enter the **API Key**.
6. (Optional) Set **Environment** to `sandbox` if the key was issued for the Rillet test environment. The default is `production`.
7. (Optional) Enter a **Start Date** in `YYYY-MM-DDTHH:MM:SSZ` format. On the first sync, incremental streams only read records updated after this time. Leave it empty to read the full history.
8. Click **Set up source**.

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Rillet** from the Source type dropdown.
4. Enter a name for the Rillet connector.
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

| Stream            | Endpoint                 | Primary key | Sync modes                |
| :---------------- | :----------------------- | :---------- | :------------------------ |
| organization      | `GET /organizations/self` | id          | Full Refresh              |
| subsidiaries      | `GET /subsidiaries`      | id          | Full Refresh              |
| accounts          | `GET /accounts`          | id          | Full Refresh, Incremental |
| books             | `GET /books`             | id          | Full Refresh              |
| book_periods      | `GET /books/periods`     | id          | Full Refresh              |
| customers         | `GET /customers`         | id          | Full Refresh, Incremental |
| customer_families | `GET /customer-families` | id          | Full Refresh              |
| products          | `GET /products`          | id          | Full Refresh              |
| contracts         | `GET /contracts`         | id          | Full Refresh              |
| invoices          | `GET /invoices`          | id          | Full Refresh, Incremental |
| invoice_payments  | `GET /invoice-payments`  | id          | Full Refresh, Incremental |
| credit_memos      | `GET /credit-memos`      | id          | Full Refresh, Incremental |
| vendors           | `GET /vendors`           | id          | Full Refresh, Incremental |
| vendor_credits    | `GET /vendor-credits`    | id          | Full Refresh, Incremental |
| bills             | `GET /bills`             | id          | Full Refresh, Incremental |
| charges           | `GET /charges`           | id          | Full Refresh, Incremental |
| reimbursements    | `GET /reimbursements`    | id          | Full Refresh, Incremental |
| journal_entries   | `GET /journal-entries`   | id          | Full Refresh, Incremental |
| bank_accounts     | `GET /bank-accounts`     | id          | Full Refresh              |
| bank_transactions | `GET /bank-transactions` | id          | Full Refresh              |
| members           | `GET /members`           | id          | Full Refresh              |

### Incremental streams

Incremental streams use the `updated_at` field as the cursor and pass the saved state to the API's `updated.gt` filter, so each sync only requests records changed since the previous one. The filter is sent with second precision. Records updated within the same second as the saved cursor can be read again, and Append + Deduped sync mode removes those duplicates.

Rillet's list endpoints that expose `updated.gt` but do not return an `updated_at` field on the record (for example `bank_transactions` and `customer_families`) are full refresh only.

### Notes

- Monetary amounts are objects with a string `amount` and a `currency`. The amount stays a string so that decimal precision is not lost.
- `book_periods` returns no records, instead of failing the sync, when the organization has no book periods (the API answers 404 in that case).

## Limitations and performance considerations

Rillet limits each API key to 600 requests per minute in production and 100 requests per minute in the test environment. The connector requests 100 records per page, runs at most 2 streams at a time, and retries HTTP 429 and 5xx responses with exponential backoff.

Rillet pagination cursors are valid for 2 hours. A single stream that takes longer than that to page through can restart from the first page.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                   |
| :------ | :--------- | :----------- | :---------------------------------------- |
| 0.1.0   | 2026-11-04 | [90964](https://github.com/airbytehq/airbyte/pull/90964) | New Source: Rillet |

</details>
