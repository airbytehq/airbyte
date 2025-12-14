# Eventee
The Airbyte connector for Eventee enables seamless integration and automated data synchronization between Eventee, a leading event management platform, and your data destinations. It extracts and transfers event-related information such as attendee details, lectures, tracks, and more. This connector ensures real-time or scheduled data flow, helping you centralize and analyze Eventee&#39;s data effortlessly for improved event insights and reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Generate it at https://admin.eventee.co/ in &#39;Settings -&gt; Features&#39;. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| halls | id | No pagination | ✅ |  ❌  |
| days | id | No pagination | ✅ |  ❌  |
| lectures | id | No pagination | ✅ |  ❌  |
| speakers | id | No pagination | ✅ |  ❌  |
| workshops | id | No pagination | ✅ |  ❌  |
| pauses | id | No pagination | ✅ |  ❌  |
| tracks | id | No pagination | ✅ |  ❌  |
| partners | id | No pagination | ✅ |  ❌  |
| participants | email | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.42 | 2025-12-09 | [70572](https://github.com/airbytehq/airbyte/pull/70572) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70187](https://github.com/airbytehq/airbyte/pull/70187) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69360](https://github.com/airbytehq/airbyte/pull/69360) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68731](https://github.com/airbytehq/airbyte/pull/68731) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68556](https://github.com/airbytehq/airbyte/pull/68556) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67742](https://github.com/airbytehq/airbyte/pull/67742) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67279](https://github.com/airbytehq/airbyte/pull/67279) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66290](https://github.com/airbytehq/airbyte/pull/66290) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65874](https://github.com/airbytehq/airbyte/pull/65874) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65243](https://github.com/airbytehq/airbyte/pull/65243) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64755](https://github.com/airbytehq/airbyte/pull/64755) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64399](https://github.com/airbytehq/airbyte/pull/64399) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63977](https://github.com/airbytehq/airbyte/pull/63977) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63608](https://github.com/airbytehq/airbyte/pull/63608) | Update dependencies |
| 0.0.28 | 2025-07-12 | [62963](https://github.com/airbytehq/airbyte/pull/62963) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62816](https://github.com/airbytehq/airbyte/pull/62816) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62316](https://github.com/airbytehq/airbyte/pull/62316) | Update dependencies |
| 0.0.25 | 2025-06-22 | [61997](https://github.com/airbytehq/airbyte/pull/61997) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61202](https://github.com/airbytehq/airbyte/pull/61202) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60349](https://github.com/airbytehq/airbyte/pull/60349) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59981](https://github.com/airbytehq/airbyte/pull/59981) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59373](https://github.com/airbytehq/airbyte/pull/59373) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58881](https://github.com/airbytehq/airbyte/pull/58881) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58302](https://github.com/airbytehq/airbyte/pull/58302) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57757](https://github.com/airbytehq/airbyte/pull/57757) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57221](https://github.com/airbytehq/airbyte/pull/57221) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56510](https://github.com/airbytehq/airbyte/pull/56510) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55986](https://github.com/airbytehq/airbyte/pull/55986) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55302](https://github.com/airbytehq/airbyte/pull/55302) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54934](https://github.com/airbytehq/airbyte/pull/54934) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54377](https://github.com/airbytehq/airbyte/pull/54377) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53780](https://github.com/airbytehq/airbyte/pull/53780) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53313](https://github.com/airbytehq/airbyte/pull/53313) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52842](https://github.com/airbytehq/airbyte/pull/52842) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52360](https://github.com/airbytehq/airbyte/pull/52360) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51646](https://github.com/airbytehq/airbyte/pull/51646) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51077](https://github.com/airbytehq/airbyte/pull/51077) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50554](https://github.com/airbytehq/airbyte/pull/50554) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50009](https://github.com/airbytehq/airbyte/pull/50009) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49470](https://github.com/airbytehq/airbyte/pull/49470) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49191](https://github.com/airbytehq/airbyte/pull/49191) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
