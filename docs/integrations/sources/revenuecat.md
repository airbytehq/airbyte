# RevenueCat
RevenueCat is a powerful and reliable in-app purchase server that makes it easy to build, analyze, and grow your subscriber base whether you&#39;re just starting out or already have millions of customers.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `start_date` | `string` | Start date.  |  |

To get started;
- You can create a new secret API key in your project settings page > API keys. Select + New.
- Give it a name, select V2 as the version, and set the following permissions:
  - `project_configuration:projects:read`
  - `project_configuration:apps:read`
  - `charts_metrics:overview:read`
  - `customer_information:customers:read`
  - `customer_information:subscriptions:read`
  - `customer_information:purchases:read`
  - `customer_information:invoices:read`
  - `project_configuration:entitlements:read`
  - `project_configuration:offerings:read`
  - `project_configuration:products:read`
- Be sure to select Generate at the top right corner.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | No pagination | ✅ |  ✅  |
| apps | id | No pagination | ✅ |  ✅  |
| metrics_overview | id | No pagination | ✅ |  ❌  |
| customers | id | No pagination | ✅ |  ✅  |
| customers_subscriptions | id | No pagination | ✅ |  ✅  |
| customers_purchases | id | No pagination | ✅ |  ✅  |
| customers_active_entitlements | entitlement_id | No pagination | ✅ |  ✅  |
| customers_aliases | id | No pagination | ✅ |  ✅  |
| customers_invoices | id | No pagination | ✅ |  ✅  |
| entitlements | id | No pagination | ✅ |  ✅  |
| entitlements_products | id.entitlement_id | No pagination | ✅ |  ✅  |
| offerings | id | No pagination | ✅ |  ✅  |
| offerings_packages | id | No pagination | ✅ |  ✅  |
| offerings_packages_products | id.package_id | No pagination | ✅ |  ✅  |
| products | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.1 | 2025-03-08 | [55546](https://github.com/airbytehq/airbyte/pull/55546) | Update dependencies |
| 0.1.0 | 2025-03-07 | [55247](https://github.com/airbytehq/airbyte/pull/55247) | Add cursor pagination, add schemas |
| 0.0.5 | 2025-03-01 | [55042](https://github.com/airbytehq/airbyte/pull/55042) | Update dependencies |
| 0.0.4 | 2025-02-23 | [54621](https://github.com/airbytehq/airbyte/pull/54621) | Update dependencies |
| 0.0.3 | 2025-02-15 | [49343](https://github.com/airbytehq/airbyte/pull/49343) | Update dependencies |
| 0.0.2 | 2024-12-11 | [47735](https://github.com/airbytehq/airbyte/pull/47735) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-09-23 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
