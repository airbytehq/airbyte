# Chift

This page contains the setup guide and reference information for the Chift source connector.

[Chift](https://www.chift.eu/) is a unified API for financial software. Its platform connects your SaaS product to accounting, invoicing, point-of-sale, and other financial tools through **consumers** (your end customers), **connections** (a consumer's link to one of those tools), and **syncs** (data flows that Chift runs between tools). This connector reads that platform metadata, plus the execution history of your syncs, from the [Chift API](https://docs.chift.eu/). It doesn't read the financial data (invoices, journal entries, and so on) that flows through those connections.

## Prerequisites

- A Chift account with access to the [Chift platform](https://chift.app/).
- A Chift API key. In the Chift platform, open the **API Keys** page and click **Add API Key**. Copy the **Client ID** and **Client Secret** when you create the key; Chift shows the client secret only once. Your **Account ID** is shown at the top left of the same page. See Chift's [Create and manage API keys](https://docs.chift.eu/developer-guides/create-api-key) guide.

Keep the following in mind when you choose or create the key:

- The key determines the environment. All keys use the same base URL, but a key created in Chift's Sandbox environment only sees sandbox consumers, and a key created in Production only sees production consumers.
- Chift lets you restrict a key to one or more consumers. If you use a restricted key, the connector only sees the data that key can access. Use an unrestricted key to sync your whole account.

## Setup guide

1. In the left navigation bar of the Airbyte UI, click **Sources**. In the top-right corner, click **+ New source**.
2. Find and select **Chift** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. Enter the **Client Id**, **Client Secret**, and **Account Id** from your Chift API key.
5. Optionally, enter a **Start Date** in `YYYY-MM-DDTHH:MM:SS` format, for example `2026-01-01T00:00:00`. Only executions that started on or after this date are synced. If you leave it empty, the connector syncs all executions. Other formats, such as a date without a time or a value with a `Z` suffix, are rejected.
6. Click **Set up source** and wait for the tests to complete.

The connector exchanges your credentials for a short-lived bearer token by calling Chift's `POST /token` endpoint at the start of each sync. If that call fails with a `401` error, check that all three values belong to the same API key and that the key hasn't been deleted.

## Supported sync modes

The Chift source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

| Stream        | Primary key    | Incremental | Chift endpoint                            |
| :------------ | :------------- | :---------- | :---------------------------------------- |
| `consumers`   | `consumerid`   | No          | `GET /consumers`                          |
| `connections` | `connectionid` | No          | `GET /consumers/{consumerid}/connections` |
| `syncs`       | `syncid`       | No          | `GET /syncs`                              |
| `executions`  | `id`           | Yes         | `GET /syncs/{syncid}/executions`          |

- `consumers` lists the consumers (your end customers) linked to your account.
- `connections` lists every connection, active or inactive, for each consumer returned by `consumers`. The `data` field is a free-form object whose keys depend on the integration the connection points to, so its contents vary from row to row.
- `syncs` lists the syncs configured for your account, including their connections, mappings, flows, and the consumers they're activated for. The `display_condition` object inside each mapping's `sub_mappings[].target_field` is also free-form.
- `executions` lists every run of each sync returned by `syncs`. Each record includes the execution `start` and `end` timestamps, its `status` (for example `IN PROGRESS`, `FINISHED`, `ERROR`, or `CANCELED`), and the `consumer_id` and `flow_id` it ran for. The stream is incremental on the `start` timestamp and pages through results 50 at a time.

`connections` and `executions` are child streams: the connector always reads `consumers` to build `connections`, and always reads `syncs` to build `executions`, even if you don't select the parent stream.

## Limitations and troubleshooting

- Chift doesn't rate limit calls to its own API, so the connector doesn't throttle requests. Chift's [rate limit documentation](https://docs.chift.eu/developer-guides/core-concepts/rate-limits) covers limits that individual third-party integrations may enforce, but those don't affect the endpoints this connector uses.
- The `executions` stream filters on the execution start time only. Executions that started before your **Start Date** are never synced, even if they finished after it.
- The `connections.data` and `syncs.mappings[].sub_mappings[].target_field.display_condition` objects have no fixed schema. Destinations that write typed files (S3 and GCS in Avro or Parquet format) store them as JSON strings. Destinations that store objects as JSON, VARIANT, or JSONB columns keep the whole object. See the [migration guide](https://docs.airbyte.com/integrations/sources/chift-migrations) for details.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-09-15 | [77576](https://github.com/airbytehq/airbyte/pull/77576) | Add `executions` stream, incremental on `start` and paginated on `page`/`size`. Declare `connections.data` and `target_field.display_condition` schemaless, matching Chift's contract, so schematizing destinations (S3/GCS Avro/Parquet) stop dropping their integration-defined keys - see the [migration guide](https://docs.airbyte.com/integrations/sources/chift-migrations) |
| 0.0.26 | 2026-09-15 | [85978](https://github.com/airbytehq/airbyte/pull/85978) | Update dependencies |
| 0.0.25 | 2026-09-08 | [85452](https://github.com/airbytehq/airbyte/pull/85452) | Update dependencies |
| 0.0.24 | 2026-08-18 | [84529](https://github.com/airbytehq/airbyte/pull/84529) | Update dependencies |
| 0.0.23 | 2026-08-11 | [83887](https://github.com/airbytehq/airbyte/pull/83887) | Update dependencies |
| 0.0.22 | 2026-08-04 | [83399](https://github.com/airbytehq/airbyte/pull/83399) | Update dependencies |
| 0.0.21 | 2026-07-28 | [82860](https://github.com/airbytehq/airbyte/pull/82860) | Update dependencies |
| 0.0.20 | 2026-07-21 | [82371](https://github.com/airbytehq/airbyte/pull/82371) | Update dependencies |
| 0.0.19 | 2026-07-14 | [81778](https://github.com/airbytehq/airbyte/pull/81778) | Update dependencies |
| 0.0.18 | 2026-06-30 | [81003](https://github.com/airbytehq/airbyte/pull/81003) | Update dependencies |
| 0.0.17 | 2026-06-23 | [80430](https://github.com/airbytehq/airbyte/pull/80430) | Update dependencies |
| 0.0.16 | 2026-06-16 | [79800](https://github.com/airbytehq/airbyte/pull/79800) | Update dependencies |
| 0.0.15 | 2026-06-09 | [79250](https://github.com/airbytehq/airbyte/pull/79250) | Update dependencies |
| 0.0.14 | 2026-06-02 | [78653](https://github.com/airbytehq/airbyte/pull/78653) | Update dependencies |
| 0.0.13 | 2026-04-28 | [77164](https://github.com/airbytehq/airbyte/pull/77164) | Update dependencies |
| 0.0.12 | 2026-04-21 | [76551](https://github.com/airbytehq/airbyte/pull/76551) | Update dependencies |
| 0.0.11 | 2026-03-31 | [75769](https://github.com/airbytehq/airbyte/pull/75769) | Update dependencies |
| 0.0.10 | 2026-03-17 | [75077](https://github.com/airbytehq/airbyte/pull/75077) | Update dependencies |
| 0.0.9 | 2026-03-10 | [74454](https://github.com/airbytehq/airbyte/pull/74454) | Update dependencies |
| 0.0.8 | 2026-02-24 | [73822](https://github.com/airbytehq/airbyte/pull/73822) | Update dependencies |
| 0.0.7 | 2026-02-17 | [73447](https://github.com/airbytehq/airbyte/pull/73447) | Update dependencies |
| 0.0.6 | 2026-02-10 | [73000](https://github.com/airbytehq/airbyte/pull/73000) | Update dependencies |
| 0.0.5 | 2026-02-03 | [72704](https://github.com/airbytehq/airbyte/pull/72704) | Update dependencies |
| 0.0.4 | 2026-01-20 | [72112](https://github.com/airbytehq/airbyte/pull/72112) | Update dependencies |
| 0.0.3 | 2026-01-14 | [71711](https://github.com/airbytehq/airbyte/pull/71711) | Update dependencies |
| 0.0.2 | 2025-12-19 | [70944](https://github.com/airbytehq/airbyte/pull/70944) | Update dependencies |
| 0.0.1 | 2025-10-13 | | Initial release by [@FVidalCarneiro](https://github.com/FVidalCarneiro) via Connector Builder |

</details>
