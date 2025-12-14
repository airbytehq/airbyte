# referralhero
[Referral Hero](https://referralhero.com) is a tool for creating, managing, and analyzing referral programs to boost customer acquisition and engagement.
With this connector, you can streamline the transfer of campaign-related data for better integration into your analytics, CRM, or marketing platforms.

Referral Hero Source Connector is a designed to sync referral data between your Referral Hero campaigns and your destination airbyte connectors.


## Generate API Token
Please follow the instructions in the following [referralhero](https://support.referralhero.com/integrate/rest-api) page to generate the api token


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | uuid | DefaultPaginator | ✅ |  ❌  |
| leaderboard |  | DefaultPaginator | ✅ |  ❌  |
| bonuses |  | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.31 | 2025-12-09 | [70585](https://github.com/airbytehq/airbyte/pull/70585) | Update dependencies |
| 0.0.30 | 2025-11-25 | [70050](https://github.com/airbytehq/airbyte/pull/70050) | Update dependencies |
| 0.0.29 | 2025-11-18 | [69593](https://github.com/airbytehq/airbyte/pull/69593) | Update dependencies |
| 0.0.28 | 2025-10-29 | [68873](https://github.com/airbytehq/airbyte/pull/68873) | Update dependencies |
| 0.0.27 | 2025-10-21 | [68363](https://github.com/airbytehq/airbyte/pull/68363) | Update dependencies |
| 0.0.26 | 2025-10-14 | [67897](https://github.com/airbytehq/airbyte/pull/67897) | Update dependencies |
| 0.0.25 | 2025-10-07 | [67540](https://github.com/airbytehq/airbyte/pull/67540) | Update dependencies |
| 0.0.24 | 2025-09-30 | [66433](https://github.com/airbytehq/airbyte/pull/66433) | Update dependencies |
| 0.0.23 | 2025-09-09 | [65669](https://github.com/airbytehq/airbyte/pull/65669) | Update dependencies |
| 0.0.22 | 2025-08-24 | [65505](https://github.com/airbytehq/airbyte/pull/65505) | Update dependencies |
| 0.0.21 | 2025-08-16 | [65005](https://github.com/airbytehq/airbyte/pull/65005) | Update dependencies |
| 0.0.20 | 2025-08-02 | [64443](https://github.com/airbytehq/airbyte/pull/64443) | Update dependencies |
| 0.0.19 | 2025-07-26 | [63995](https://github.com/airbytehq/airbyte/pull/63995) | Update dependencies |
| 0.0.18 | 2025-07-20 | [63659](https://github.com/airbytehq/airbyte/pull/63659) | Update dependencies |
| 0.0.17 | 2025-07-05 | [62698](https://github.com/airbytehq/airbyte/pull/62698) | Update dependencies |
| 0.0.16 | 2025-06-28 | [62274](https://github.com/airbytehq/airbyte/pull/62274) | Update dependencies |
| 0.0.15 | 2025-06-21 | [61799](https://github.com/airbytehq/airbyte/pull/61799) | Update dependencies |
| 0.0.14 | 2025-06-14 | [61315](https://github.com/airbytehq/airbyte/pull/61315) | Update dependencies |
| 0.0.13 | 2025-05-24 | [60536](https://github.com/airbytehq/airbyte/pull/60536) | Update dependencies |
| 0.0.12 | 2025-05-10 | [60054](https://github.com/airbytehq/airbyte/pull/60054) | Update dependencies |
| 0.0.11 | 2025-05-03 | [59454](https://github.com/airbytehq/airbyte/pull/59454) | Update dependencies |
| 0.0.10 | 2025-04-27 | [59041](https://github.com/airbytehq/airbyte/pull/59041) | Update dependencies |
| 0.0.9 | 2025-04-19 | [58457](https://github.com/airbytehq/airbyte/pull/58457) | Update dependencies |
| 0.0.8 | 2025-04-12 | [57954](https://github.com/airbytehq/airbyte/pull/57954) | Update dependencies |
| 0.0.7 | 2025-04-05 | [57365](https://github.com/airbytehq/airbyte/pull/57365) | Update dependencies |
| 0.0.6 | 2025-03-29 | [56724](https://github.com/airbytehq/airbyte/pull/56724) | Update dependencies |
| 0.0.5 | 2025-03-22 | [56184](https://github.com/airbytehq/airbyte/pull/56184) | Update dependencies |
| 0.0.4 | 2025-03-08 | [55070](https://github.com/airbytehq/airbyte/pull/55070) | Update dependencies |
| 0.0.3 | 2025-02-23 | [54597](https://github.com/airbytehq/airbyte/pull/54597) | Update dependencies |
| 0.0.2 | 2025-02-15 | [47509](https://github.com/airbytehq/airbyte/pull/47509) | Update dependencies |
| 0.0.1 | 2024-10-07 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
