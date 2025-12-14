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
| 0.1.26 | 2025-12-09 | [70606](https://github.com/airbytehq/airbyte/pull/70606) | Update dependencies |
| 0.1.25 | 2025-11-25 | [70038](https://github.com/airbytehq/airbyte/pull/70038) | Update dependencies |
| 0.1.24 | 2025-11-18 | [69602](https://github.com/airbytehq/airbyte/pull/69602) | Update dependencies |
| 0.1.23 | 2025-10-29 | [68863](https://github.com/airbytehq/airbyte/pull/68863) | Update dependencies |
| 0.1.22 | 2025-10-21 | [68339](https://github.com/airbytehq/airbyte/pull/68339) | Update dependencies |
| 0.1.21 | 2025-10-14 | [67895](https://github.com/airbytehq/airbyte/pull/67895) | Update dependencies |
| 0.1.20 | 2025-10-07 | [67536](https://github.com/airbytehq/airbyte/pull/67536) | Update dependencies |
| 0.1.19 | 2025-09-30 | [66440](https://github.com/airbytehq/airbyte/pull/66440) | Update dependencies |
| 0.1.18 | 2025-09-09 | [65665](https://github.com/airbytehq/airbyte/pull/65665) | Update dependencies |
| 0.1.17 | 2025-08-23 | [65424](https://github.com/airbytehq/airbyte/pull/65424) | Update dependencies |
| 0.1.16 | 2025-08-16 | [65028](https://github.com/airbytehq/airbyte/pull/65028) | Update dependencies |
| 0.1.15 | 2025-08-02 | [64427](https://github.com/airbytehq/airbyte/pull/64427) | Update dependencies |
| 0.1.14 | 2025-07-26 | [64007](https://github.com/airbytehq/airbyte/pull/64007) | Update dependencies |
| 0.1.13 | 2025-07-19 | [63631](https://github.com/airbytehq/airbyte/pull/63631) | Update dependencies |
| 0.1.12 | 2025-07-05 | [62718](https://github.com/airbytehq/airbyte/pull/62718) | Update dependencies |
| 0.1.11 | 2025-06-28 | [62229](https://github.com/airbytehq/airbyte/pull/62229) | Update dependencies |
| 0.1.10 | 2025-06-21 | [61796](https://github.com/airbytehq/airbyte/pull/61796) | Update dependencies |
| 0.1.9 | 2025-05-25 | [60465](https://github.com/airbytehq/airbyte/pull/60465) | Update dependencies |
| 0.1.8 | 2025-05-10 | [60077](https://github.com/airbytehq/airbyte/pull/60077) | Update dependencies |
| 0.1.7 | 2025-05-04 | [59029](https://github.com/airbytehq/airbyte/pull/59029) | Update dependencies |
| 0.1.6 | 2025-04-19 | [58421](https://github.com/airbytehq/airbyte/pull/58421) | Update dependencies |
| 0.1.5 | 2025-04-12 | [57966](https://github.com/airbytehq/airbyte/pull/57966) | Update dependencies |
| 0.1.4 | 2025-04-05 | [57293](https://github.com/airbytehq/airbyte/pull/57293) | Update dependencies |
| 0.1.3 | 2025-03-29 | [56757](https://github.com/airbytehq/airbyte/pull/56757) | Update dependencies |
| 0.1.2 | 2025-03-22 | [56229](https://github.com/airbytehq/airbyte/pull/56229) | Update dependencies |
| 0.1.1 | 2025-03-08 | [55546](https://github.com/airbytehq/airbyte/pull/55546) | Update dependencies |
| 0.1.0 | 2025-03-07 | [55247](https://github.com/airbytehq/airbyte/pull/55247) | Add cursor pagination, add schemas |
| 0.0.5 | 2025-03-01 | [55042](https://github.com/airbytehq/airbyte/pull/55042) | Update dependencies |
| 0.0.4 | 2025-02-23 | [54621](https://github.com/airbytehq/airbyte/pull/54621) | Update dependencies |
| 0.0.3 | 2025-02-15 | [49343](https://github.com/airbytehq/airbyte/pull/49343) | Update dependencies |
| 0.0.2 | 2024-12-11 | [47735](https://github.com/airbytehq/airbyte/pull/47735) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-09-23 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
