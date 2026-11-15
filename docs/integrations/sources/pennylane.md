# Pennylane

This connector reads invoices, estimates, customers, suppliers, products, plan items, and categories from the [Pennylane Company API v1](https://pennylane.readme.io/v1.0/reference).

:::warning API v1 is deprecated

This connector uses `/api/external/v1/`, not API v2. Pennylane's [migration guide](https://pennylane.readme.io/docs/api-v2-vs-v1) states that v1 was scheduled for deprecation by the end of 2025 and that v2 is the stable API. Confirm that your company still has v1 access before configuring this connector. A v2 token alone does not provide the v1 scopes this connector requires.

:::

## Prerequisites

You need a Pennylane company API token with access to API v1. The connector sends this token as a bearer token; it does not perform an OAuth authorization flow or refresh tokens.

Grant the following [v1 scopes](https://pennylane.readme.io/v1.0/docs/v1-scopes) for the streams you want to sync:

| Scope | Streams |
| --- | --- |
| `supplier_invoices` | `supplier_invoices`, `suppliers` |
| `customer_invoices` | `customer_invoices`, `customer_estimates`, `customers`, `products`, `plan_items` |
| `accounting` | `categories`, `category_groups` |

The connection check reads `supplier_invoices`, so your token needs the `supplier_invoices` scope even if you only plan to sync other streams.

See Pennylane's [token management guide](https://pennylane.readme.io/docs/generating-my-api-token) for account requirements and token settings. That guide describes the current v2 API; make sure the token you use here has the legacy v1 scopes above.

## Setup guide

1. In Airbyte, create a source and select **Pennylane**.
2. Enter a name for the source.
3. Set **Start time** to the earliest record update time you want to sync, in UTC, using the format `YYYY-MM-DDTHH:mm:ssZ`, for example, `2024-01-01T00:00:00Z`.
4. Enter your Pennylane token in **API Key**.
5. Select **Set up source** and wait for the connection check to complete.

## Configuration

Both settings are required and have no default value.

| Input | Type | Description |
| --- | --- | --- |
| `start_time` | `string` | Initial lower bound for `updated_at` on streams that support incremental sync. Use UTC in the format `YYYY-MM-DDTHH:mm:ssZ`. Records created before this time can still be synced if they were updated on or after it. |
| `api_key` | `string` | Pennylane company API token with the required v1 scopes. |

## Streams

| Stream | Primary key | Full refresh | Incremental |
| --- | --- | --- | --- |
| `supplier_invoices` | `id` | Yes | Yes |
| `suppliers` | `source_id` | Yes | Yes |
| `plan_items` | `v2_id` | Yes | No |
| `customers` | `source_id` | Yes | Yes |
| `customer_invoices` | `id` | Yes | Yes |
| `customer_estimates` | `id` | Yes | Yes |
| `products` | `source_id` | Yes | Yes |
| `category_groups` | `id` | Yes | No |
| `categories` | `source_id` | Yes | Yes |

### Sync behavior

Incremental streams use `updated_at` as their cursor. The first sync reads records updated on or after **Start time**. Later incremental syncs resume from the saved cursor. Because the lower bound is inclusive, records at the cursor timestamp can be read again.

`plan_items` and `category_groups` do not use **Start time** and are read in full on every sync. All streams follow the API's `current_page` and `total_pages` response fields, including when a page contains fewer records than requested.

## Rate limits and troubleshooting

Pennylane's [v1 rate limit](https://pennylane.readme.io/v1.0/docs/rate-limiting-1) is 5 requests per second per token, across all endpoints, in both production and sandbox environments. Requests from other integrations using the same token count toward this limit. Exceeding it returns HTTP `429`.

- If the connection check returns HTTP `401`, verify that the token is valid and has not expired or been revoked.
- If it returns HTTP `403`, verify the token's v1 scopes, especially `supplier_invoices`, which is required for the connection check. Access to other streams depends on their scopes listed above.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.4.0 | 2026-11-15 | [91541](https://github.com/airbytehq/airbyte/pull/91541) | Paginate on `current_page`/`total_pages` instead of stopping on a short page. Add missing `customer_invoices` and `customers` fields, suggested streams, and a 1-hour heartbeat timeout (`maxSecondsBetweenMessages: 3600`) |
| 0.3.53 | 2026-11-10 | [91670](https://github.com/airbytehq/airbyte/pull/91670) | Update dependencies |
| 0.3.52 | 2026-11-03 | [90689](https://github.com/airbytehq/airbyte/pull/90689) | Update dependencies |
| 0.3.51 | 2026-10-27 | [90031](https://github.com/airbytehq/airbyte/pull/90031) | Update dependencies |
| 0.3.50 | 2026-10-20 | [89272](https://github.com/airbytehq/airbyte/pull/89272) | Update dependencies |
| 0.3.49 | 2026-10-13 | [88731](https://github.com/airbytehq/airbyte/pull/88731) | Update dependencies |
| 0.3.48 | 2026-10-06 | [87962](https://github.com/airbytehq/airbyte/pull/87962) | Update dependencies |
| 0.3.47 | 2026-09-29 | [87285](https://github.com/airbytehq/airbyte/pull/87285) | Update dependencies |
| 0.3.46 | 2026-09-22 | [86766](https://github.com/airbytehq/airbyte/pull/86766) | Update dependencies |
| 0.3.45 | 2026-09-15 | [86181](https://github.com/airbytehq/airbyte/pull/86181) | Update dependencies |
| 0.3.44 | 2026-09-08 | [85620](https://github.com/airbytehq/airbyte/pull/85620) | Update dependencies |
| 0.3.43 | 2026-08-18 | [84697](https://github.com/airbytehq/airbyte/pull/84697) | Update dependencies |
| 0.3.42 | 2026-08-11 | [84056](https://github.com/airbytehq/airbyte/pull/84056) | Update dependencies |
| 0.3.41 | 2026-08-04 | [83565](https://github.com/airbytehq/airbyte/pull/83565) | Update dependencies |
| 0.3.40 | 2026-07-28 | [83051](https://github.com/airbytehq/airbyte/pull/83051) | Update dependencies |
| 0.3.39 | 2026-07-21 | [82543](https://github.com/airbytehq/airbyte/pull/82543) | Update dependencies |
| 0.3.38 | 2026-07-14 | [81943](https://github.com/airbytehq/airbyte/pull/81943) | Update dependencies |
| 0.3.37 | 2026-06-30 | [81174](https://github.com/airbytehq/airbyte/pull/81174) | Update dependencies |
| 0.3.36 | 2026-06-23 | [80572](https://github.com/airbytehq/airbyte/pull/80572) | Update dependencies |
| 0.3.35 | 2026-06-16 | [79988](https://github.com/airbytehq/airbyte/pull/79988) | Update dependencies |
| 0.3.34 | 2026-06-09 | [79463](https://github.com/airbytehq/airbyte/pull/79463) | Update dependencies |
| 0.3.33 | 2026-06-02 | [78873](https://github.com/airbytehq/airbyte/pull/78873) | Update dependencies |
| 0.3.32 | 2026-04-28 | [77368](https://github.com/airbytehq/airbyte/pull/77368) | Update dependencies |
| 0.3.31 | 2026-04-21 | [76695](https://github.com/airbytehq/airbyte/pull/76695) | Update dependencies |
| 0.3.30 | 2026-03-31 | [75817](https://github.com/airbytehq/airbyte/pull/75817) | Update dependencies |
| 0.3.29 | 2026-03-17 | [75030](https://github.com/airbytehq/airbyte/pull/75030) | Update dependencies |
| 0.3.28 | 2026-03-10 | [74480](https://github.com/airbytehq/airbyte/pull/74480) | Update dependencies |
| 0.3.27 | 2026-02-24 | [73839](https://github.com/airbytehq/airbyte/pull/73839) | Update dependencies |
| 0.3.26 | 2026-02-17 | [73193](https://github.com/airbytehq/airbyte/pull/73193) | Update dependencies |
| 0.3.25 | 2026-02-03 | [72664](https://github.com/airbytehq/airbyte/pull/72664) | Update dependencies |
| 0.3.24 | 2026-01-20 | [72189](https://github.com/airbytehq/airbyte/pull/72189) | Update dependencies |
| 0.3.23 | 2026-01-14 | [71545](https://github.com/airbytehq/airbyte/pull/71545) | Update dependencies |
| 0.3.22 | 2025-12-18 | [70487](https://github.com/airbytehq/airbyte/pull/70487) | Update dependencies |
| 0.3.21 | 2025-11-25 | [69972](https://github.com/airbytehq/airbyte/pull/69972) | Update dependencies |
| 0.3.20 | 2025-11-18 | [69617](https://github.com/airbytehq/airbyte/pull/69617) | Update dependencies |
| 0.3.19 | 2025-10-29 | [68995](https://github.com/airbytehq/airbyte/pull/68995) | Update dependencies |
| 0.3.18 | 2025-10-21 | [68262](https://github.com/airbytehq/airbyte/pull/68262) | Update dependencies |
| 0.3.17 | 2025-10-14 | [67795](https://github.com/airbytehq/airbyte/pull/67795) | Update dependencies |
| 0.3.16 | 2025-10-07 | [67346](https://github.com/airbytehq/airbyte/pull/67346) | Update dependencies |
| 0.3.15 | 2025-10-01 | [66965](https://github.com/airbytehq/airbyte/pull/66965) | Update dependencies |
| 0.3.14 | 2025-09-23 | [66425](https://github.com/airbytehq/airbyte/pull/66425) | Update dependencies |
| 0.3.13 | 2025-09-10 | [65753](https://github.com/airbytehq/airbyte/pull/65753) | Update dependencies |
| 0.3.12 | 2025-08-23 | [65220](https://github.com/airbytehq/airbyte/pull/65220) | Update dependencies |
| 0.3.11 | 2025-08-09 | [64769](https://github.com/airbytehq/airbyte/pull/64769) | Update dependencies |
| 0.3.10 | 2025-08-02 | [64225](https://github.com/airbytehq/airbyte/pull/64225) | Update dependencies |
| 0.3.9 | 2025-07-26 | [63817](https://github.com/airbytehq/airbyte/pull/63817) | Update dependencies |
| 0.3.8 | 2025-07-19 | [63404](https://github.com/airbytehq/airbyte/pull/63404) | Update dependencies |
| 0.3.7 | 2025-07-12 | [63196](https://github.com/airbytehq/airbyte/pull/63196) | Update dependencies |
| 0.3.6 | 2025-07-05 | [62622](https://github.com/airbytehq/airbyte/pull/62622) | Update dependencies |
| 0.3.5 | 2025-06-28 | [62387](https://github.com/airbytehq/airbyte/pull/62387) | Update dependencies |
| 0.3.4 | 2025-06-21 | [61925](https://github.com/airbytehq/airbyte/pull/61925) | Update dependencies |
| 0.3.3 | 2025-06-14 | [61062](https://github.com/airbytehq/airbyte/pull/61062) | Update dependencies |
| 0.3.2 | 2025-05-24 | [60575](https://github.com/airbytehq/airbyte/pull/60575) | Update dependencies |
| 0.3.1 | 2025-05-10 | [60071](https://github.com/airbytehq/airbyte/pull/60071) | Update dependencies |
| 0.3.0 | 2025-05-09 | [59679](https://github.com/airbytehq/airbyte/pull/59679) | Add  stream `customer_estimates` stream |
| 0.2.9 | 2025-05-03 | [59078](https://github.com/airbytehq/airbyte/pull/59078) | Update dependencies |
| 0.2.8 | 2025-04-19 | [57882](https://github.com/airbytehq/airbyte/pull/57882) | Update dependencies |
| 0.2.7 | 2025-04-05 | [57347](https://github.com/airbytehq/airbyte/pull/57347) | Update dependencies |
| 0.2.6 | 2025-03-29 | [56788](https://github.com/airbytehq/airbyte/pull/56788) | Update dependencies |
| 0.2.5 | 2025-03-22 | [56221](https://github.com/airbytehq/airbyte/pull/56221) | Update dependencies |
| 0.2.4 | 2025-03-08 | [55556](https://github.com/airbytehq/airbyte/pull/55556) | Update dependencies |
| 0.2.3 | 2025-03-01 | [55024](https://github.com/airbytehq/airbyte/pull/55024) | Update dependencies |
| 0.2.2 | 2025-02-23 | [54601](https://github.com/airbytehq/airbyte/pull/54601) | Update dependencies |
| 0.2.1 | 2025-02-15 | [50686](https://github.com/airbytehq/airbyte/pull/50686) | Update dependencies |
| 0.2.0 | 2025-01-29 | [52596](https://github.com/airbytehq/airbyte/pull/52596) | Fixes for category_groups and plan_items |
| 0.1.1 | 2024-12-21 | [50294](https://github.com/airbytehq/airbyte/pull/50294) | Update dependencies |
| 0.1.0 | 2024-12-10 | [48892](https://github.com/airbytehq/airbyte/pull/48892) | Add missing fields to `customer_invoices` stream |
| 0.0.6 | 2024-12-14 | [49659](https://github.com/airbytehq/airbyte/pull/49659) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49322](https://github.com/airbytehq/airbyte/pull/49322) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49053](https://github.com/airbytehq/airbyte/pull/49053) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47902](https://github.com/airbytehq/airbyte/pull/47902) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47536](https://github.com/airbytehq/airbyte/pull/47536) | Update dependencies |
| 0.0.1 | 2024-08-21 | | Initial release by natikgadzhi via Connector Builder |

</details>
