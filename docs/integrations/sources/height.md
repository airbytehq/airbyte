# Height

This page contains the setup guide and reference information for the Height source connector.

## Prerequisites

To set up the Height source connector, you'll need the Height API key that you could see once you login and navigate to https://height.app/xxxxx/settings/api, and copy your secret key
Website: https://height.app

API Documentation: https://height.notion.site/API-documentation-643aea5bf01742de9232e5971cb4afda

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API secret which is copied from the settings page of height.app  |  |
| `start_date` | `string` | Start date for incremental sync supported streams |  |
| `search_query` | `string` | search_query. Search query to be used with search stream | task |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| workspace | id | No pagination | ✅ |  ✅  |
| lists | id | No pagination | ✅ |  ✅  |
| tasks | id | No pagination | ✅ |  ✅  |
| activities | id | No pagination | ✅ |  ✅  |
| field_templates | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ✅  |
| groups | id | No pagination | ✅ |  ✅  |
| search | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | ---- | ---------------- |
| 0.0.44 | 2025-12-09 | [70500](https://github.com/airbytehq/airbyte/pull/70500) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70082](https://github.com/airbytehq/airbyte/pull/70082) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69371](https://github.com/airbytehq/airbyte/pull/69371) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68806](https://github.com/airbytehq/airbyte/pull/68806) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68258](https://github.com/airbytehq/airbyte/pull/68258) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67881](https://github.com/airbytehq/airbyte/pull/67881) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67406](https://github.com/airbytehq/airbyte/pull/67406) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66396](https://github.com/airbytehq/airbyte/pull/66396) | Update dependencies |
| 0.0.36 | 2025-09-09 | [66074](https://github.com/airbytehq/airbyte/pull/66074) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65346](https://github.com/airbytehq/airbyte/pull/65346) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64605](https://github.com/airbytehq/airbyte/pull/64605) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64279](https://github.com/airbytehq/airbyte/pull/64279) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63521](https://github.com/airbytehq/airbyte/pull/63521) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63126](https://github.com/airbytehq/airbyte/pull/63126) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62600](https://github.com/airbytehq/airbyte/pull/62600) | Update dependencies |
| 0.0.29 | 2025-06-21 | [61827](https://github.com/airbytehq/airbyte/pull/61827) | Update dependencies |
| 0.0.28 | 2025-06-14 | [61082](https://github.com/airbytehq/airbyte/pull/61082) | Update dependencies |
| 0.0.27 | 2025-05-24 | [60680](https://github.com/airbytehq/airbyte/pull/60680) | Update dependencies |
| 0.0.26 | 2025-05-10 | [59788](https://github.com/airbytehq/airbyte/pull/59788) | Update dependencies |
| 0.0.25 | 2025-05-03 | [59261](https://github.com/airbytehq/airbyte/pull/59261) | Update dependencies |
| 0.0.24 | 2025-04-26 | [58821](https://github.com/airbytehq/airbyte/pull/58821) | Update dependencies |
| 0.0.23 | 2025-04-19 | [58219](https://github.com/airbytehq/airbyte/pull/58219) | Update dependencies |
| 0.0.22 | 2025-04-12 | [57733](https://github.com/airbytehq/airbyte/pull/57733) | Update dependencies |
| 0.0.21 | 2025-04-05 | [57076](https://github.com/airbytehq/airbyte/pull/57076) | Update dependencies |
| 0.0.20 | 2025-03-29 | [56710](https://github.com/airbytehq/airbyte/pull/56710) | Update dependencies |
| 0.0.19 | 2025-03-22 | [56065](https://github.com/airbytehq/airbyte/pull/56065) | Update dependencies |
| 0.0.18 | 2025-03-08 | [55435](https://github.com/airbytehq/airbyte/pull/55435) | Update dependencies |
| 0.0.17 | 2025-03-01 | [54801](https://github.com/airbytehq/airbyte/pull/54801) | Update dependencies |
| 0.0.16 | 2025-02-22 | [54288](https://github.com/airbytehq/airbyte/pull/54288) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53793](https://github.com/airbytehq/airbyte/pull/53793) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53247](https://github.com/airbytehq/airbyte/pull/53247) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52741](https://github.com/airbytehq/airbyte/pull/52741) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52264](https://github.com/airbytehq/airbyte/pull/52264) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51836](https://github.com/airbytehq/airbyte/pull/51836) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51154](https://github.com/airbytehq/airbyte/pull/51154) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50610](https://github.com/airbytehq/airbyte/pull/50610) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50094](https://github.com/airbytehq/airbyte/pull/50094) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49597](https://github.com/airbytehq/airbyte/pull/49597) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49225](https://github.com/airbytehq/airbyte/pull/49225) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48977](https://github.com/airbytehq/airbyte/pull/48977) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48158](https://github.com/airbytehq/airbyte/pull/48158) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47790](https://github.com/airbytehq/airbyte/pull/47790) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47615](https://github.com/airbytehq/airbyte/pull/47615) | Update dependencies |
| 0.0.1 | 2024-08-31 | [45065](https://github.com/airbytehq/airbyte/pull/45065) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
