# UpPromote
The Uppromote Connector for Airbyte enables seamless data integration between Uppromote, an affiliate and influencer marketing platform, and your data warehouses or analytics tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. For developing your own custom integration with UpPromote, you can create an API key. This is available from Professional plan.  Simply go to Settings > Integration > API > Create API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| affiliates | id | DefaultPaginator | ✅ |  ❌  |
| coupons | id | DefaultPaginator | ✅ |  ❌  |
| referrals | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.25 | 2025-06-15 | [61227](https://github.com/airbytehq/airbyte/pull/61227) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60743](https://github.com/airbytehq/airbyte/pull/60743) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59959](https://github.com/airbytehq/airbyte/pull/59959) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59554](https://github.com/airbytehq/airbyte/pull/59554) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58956](https://github.com/airbytehq/airbyte/pull/58956) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58551](https://github.com/airbytehq/airbyte/pull/58551) | Update dependencies |
| 0.0.19 | 2025-04-13 | [58055](https://github.com/airbytehq/airbyte/pull/58055) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57427](https://github.com/airbytehq/airbyte/pull/57427) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56863](https://github.com/airbytehq/airbyte/pull/56863) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56298](https://github.com/airbytehq/airbyte/pull/56298) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55637](https://github.com/airbytehq/airbyte/pull/55637) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55093](https://github.com/airbytehq/airbyte/pull/55093) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54507](https://github.com/airbytehq/airbyte/pull/54507) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54054](https://github.com/airbytehq/airbyte/pull/54054) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53583](https://github.com/airbytehq/airbyte/pull/53583) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53035](https://github.com/airbytehq/airbyte/pull/53035) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52421](https://github.com/airbytehq/airbyte/pull/52421) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51951](https://github.com/airbytehq/airbyte/pull/51951) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51385](https://github.com/airbytehq/airbyte/pull/51385) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50784](https://github.com/airbytehq/airbyte/pull/50784) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50343](https://github.com/airbytehq/airbyte/pull/50343) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49401](https://github.com/airbytehq/airbyte/pull/49401) | Update dependencies |
| 0.0.3 | 2024-11-04 | [47828](https://github.com/airbytehq/airbyte/pull/47828) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47589](https://github.com/airbytehq/airbyte/pull/47589) | Update dependencies |
| 0.0.1 | 2024-10-10 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
