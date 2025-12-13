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
| 0.0.44 | 2025-12-09 | [70684](https://github.com/airbytehq/airbyte/pull/70684) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70146](https://github.com/airbytehq/airbyte/pull/70146) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69688](https://github.com/airbytehq/airbyte/pull/69688) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68851](https://github.com/airbytehq/airbyte/pull/68851) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68555](https://github.com/airbytehq/airbyte/pull/68555) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67854](https://github.com/airbytehq/airbyte/pull/67854) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67505](https://github.com/airbytehq/airbyte/pull/67505) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66837](https://github.com/airbytehq/airbyte/pull/66837) | Update dependencies |
| 0.0.36 | 2025-09-23 | [66604](https://github.com/airbytehq/airbyte/pull/66604) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65680](https://github.com/airbytehq/airbyte/pull/65680) | Update dependencies |
| 0.0.34 | 2025-08-24 | [65471](https://github.com/airbytehq/airbyte/pull/65471) | Update dependencies |
| 0.0.33 | 2025-08-09 | [64869](https://github.com/airbytehq/airbyte/pull/64869) | Update dependencies |
| 0.0.32 | 2025-08-02 | [64375](https://github.com/airbytehq/airbyte/pull/64375) | Update dependencies |
| 0.0.31 | 2025-07-26 | [64078](https://github.com/airbytehq/airbyte/pull/64078) | Update dependencies |
| 0.0.30 | 2025-07-20 | [63683](https://github.com/airbytehq/airbyte/pull/63683) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63173](https://github.com/airbytehq/airbyte/pull/63173) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62738](https://github.com/airbytehq/airbyte/pull/62738) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62227](https://github.com/airbytehq/airbyte/pull/62227) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61758](https://github.com/airbytehq/airbyte/pull/61758) | Update dependencies |
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
