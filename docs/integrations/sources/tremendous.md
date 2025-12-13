# Tremendous
Tremendous connector  enables seamless integration with Tremendous API. This connector allows organizations to automate and sync reward, incentive, and payout data, tapping into 2000+ payout methods, including ACH, gift cards, PayPal, and prepaid cards, all from a single platform.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. You can generate an API key through the Tremendous dashboard under Team Settings &gt; Developers. Save the key once you’ve generated it. |  |
| `environment` | `string` | Environment.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| funding_sources | id | DefaultPaginator | ✅ |  ❌  |
| account_members | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| exchange_rates |  | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| balance_transactions |  | DefaultPaginator | ✅ |  ❌  |
| rewards | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70743](https://github.com/airbytehq/airbyte/pull/70743) | Update dependencies |
| 0.0.42 | 2025-11-25 | [69894](https://github.com/airbytehq/airbyte/pull/69894) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69693](https://github.com/airbytehq/airbyte/pull/69693) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68878](https://github.com/airbytehq/airbyte/pull/68878) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68551](https://github.com/airbytehq/airbyte/pull/68551) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67862](https://github.com/airbytehq/airbyte/pull/67862) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67502](https://github.com/airbytehq/airbyte/pull/67502) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66829](https://github.com/airbytehq/airbyte/pull/66829) | Update dependencies |
| 0.0.35 | 2025-09-23 | [66606](https://github.com/airbytehq/airbyte/pull/66606) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65730](https://github.com/airbytehq/airbyte/pull/65730) | Update dependencies |
| 0.0.33 | 2025-08-24 | [65442](https://github.com/airbytehq/airbyte/pull/65442) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64854](https://github.com/airbytehq/airbyte/pull/64854) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64328](https://github.com/airbytehq/airbyte/pull/64328) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64061](https://github.com/airbytehq/airbyte/pull/64061) | Update dependencies |
| 0.0.29 | 2025-07-20 | [63687](https://github.com/airbytehq/airbyte/pull/63687) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63203](https://github.com/airbytehq/airbyte/pull/63203) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62707](https://github.com/airbytehq/airbyte/pull/62707) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62260](https://github.com/airbytehq/airbyte/pull/62260) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61465](https://github.com/airbytehq/airbyte/pull/61465) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60491](https://github.com/airbytehq/airbyte/pull/60491) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60073](https://github.com/airbytehq/airbyte/pull/60073) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59573](https://github.com/airbytehq/airbyte/pull/59573) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59003](https://github.com/airbytehq/airbyte/pull/59003) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58452](https://github.com/airbytehq/airbyte/pull/58452) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57971](https://github.com/airbytehq/airbyte/pull/57971) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57447](https://github.com/airbytehq/airbyte/pull/57447) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56899](https://github.com/airbytehq/airbyte/pull/56899) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56311](https://github.com/airbytehq/airbyte/pull/56311) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55597](https://github.com/airbytehq/airbyte/pull/55597) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55108](https://github.com/airbytehq/airbyte/pull/55108) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54467](https://github.com/airbytehq/airbyte/pull/54467) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54057](https://github.com/airbytehq/airbyte/pull/54057) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53566](https://github.com/airbytehq/airbyte/pull/53566) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53065](https://github.com/airbytehq/airbyte/pull/53065) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52446](https://github.com/airbytehq/airbyte/pull/52446) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51945](https://github.com/airbytehq/airbyte/pull/51945) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51406](https://github.com/airbytehq/airbyte/pull/51406) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50768](https://github.com/airbytehq/airbyte/pull/50768) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50363](https://github.com/airbytehq/airbyte/pull/50363) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49750](https://github.com/airbytehq/airbyte/pull/49750) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49375](https://github.com/airbytehq/airbyte/pull/49375) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49128](https://github.com/airbytehq/airbyte/pull/49128) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-29 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
