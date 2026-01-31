# Chift

[Chift](https://www.chift.eu/) is a unified API platform that enables SaaS products to embed financial connectivity. It provides a single integration point to connect with accounting, invoicing, eCommerce, point of sale (POS), payment, banking, and property management system (PMS) software used by your customers.

This connector allows you to sync data from your Chift account, including information about your consumers, their connections, and configured syncs.

## Prerequisites

To use this connector, you need a Chift account with API access. You can obtain your API credentials from the [Chift dashboard](https://chift.app/).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. Your Chift API client identifier. |  |
| `account_id` | `string` | Account ID. Your Chift account identifier. |  |
| `client_secret` | `string` | Client Secret. Your Chift API client secret. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| consumers | consumerid | No pagination | ✅ |  ❌  |
| connections | connectionid | No pagination | ✅ |  ❌  |
| syncs | syncid | No pagination | ✅ |  ❌  |

### Stream details

The **consumers** stream contains information about end-users who have the ability to connect their financial software through your Chift integration. Each consumer represents a customer of your SaaS product.

The **connections** stream contains the active integrations between your consumers and their financial software. Each connection represents a link between a consumer and a specific accounting, invoicing, or other supported tool.

The **syncs** stream contains information about configured data synchronization flows. Syncs are pre-built automation flows that move data between connected systems.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2026-01-20 | [72112](https://github.com/airbytehq/airbyte/pull/72112) | Update dependencies |
| 0.0.3 | 2026-01-14 | [71711](https://github.com/airbytehq/airbyte/pull/71711) | Update dependencies |
| 0.0.2 | 2025-12-19 | [70944](https://github.com/airbytehq/airbyte/pull/70944) | Update dependencies |
| 0.0.1 | 2025-10-13 | | Initial release by [@FVidalCarneiro](https://github.com/FVidalCarneiro) via Connector Builder |

</details>
