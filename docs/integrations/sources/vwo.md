# VWO
This directory contains the manifest-only connector for [`source-vwo`](https://app.vwo.com/).

## Documentation reference:
Visit `https://developers.vwo.com/reference/introduction-1` for API documentation

## Authentication setup
`VWO` uses API token authentication, Visit `https://app.vwo.com/#/developers/tokens` for getting your api token. Refer `https://developers.vwo.com/reference/authentication-for-personal-use-of-api-1`.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| accounts_feeds | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| smartcode | uid | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| custom_widgets | id | DefaultPaginator | ✅ |  ✅  |
| thresholds | uid | DefaultPaginator | ✅ |  ❌  |
| integrations | uid | DefaultPaginator | ✅ |  ❌  |
| labels | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.43 | 2025-12-09 | [70710](https://github.com/airbytehq/airbyte/pull/70710) | Update dependencies |
| 0.0.42 | 2025-11-25 | [70172](https://github.com/airbytehq/airbyte/pull/70172) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69680](https://github.com/airbytehq/airbyte/pull/69680) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68977](https://github.com/airbytehq/airbyte/pull/68977) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68342](https://github.com/airbytehq/airbyte/pull/68342) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67954](https://github.com/airbytehq/airbyte/pull/67954) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67326](https://github.com/airbytehq/airbyte/pull/67326) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66452](https://github.com/airbytehq/airbyte/pull/66452) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65671](https://github.com/airbytehq/airbyte/pull/65671) | Update dependencies |
| 0.0.34 | 2025-08-24 | [65461](https://github.com/airbytehq/airbyte/pull/65461) | Update dependencies |
| 0.0.33 | 2025-08-09 | [64862](https://github.com/airbytehq/airbyte/pull/64862) | Update dependencies |
| 0.0.32 | 2025-08-02 | [64381](https://github.com/airbytehq/airbyte/pull/64381) | Update dependencies |
| 0.0.31 | 2025-07-26 | [64080](https://github.com/airbytehq/airbyte/pull/64080) | Update dependencies |
| 0.0.30 | 2025-07-20 | [63682](https://github.com/airbytehq/airbyte/pull/63682) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63215](https://github.com/airbytehq/airbyte/pull/63215) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62737](https://github.com/airbytehq/airbyte/pull/62737) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62258](https://github.com/airbytehq/airbyte/pull/62258) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61778](https://github.com/airbytehq/airbyte/pull/61778) | Update dependencies |
| 0.0.25 | 2025-06-15 | [61172](https://github.com/airbytehq/airbyte/pull/61172) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60776](https://github.com/airbytehq/airbyte/pull/60776) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59934](https://github.com/airbytehq/airbyte/pull/59934) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59535](https://github.com/airbytehq/airbyte/pull/59535) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58932](https://github.com/airbytehq/airbyte/pull/58932) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58559](https://github.com/airbytehq/airbyte/pull/58559) | Update dependencies |
| 0.0.19 | 2025-04-12 | [58029](https://github.com/airbytehq/airbyte/pull/58029) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57467](https://github.com/airbytehq/airbyte/pull/57467) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56811](https://github.com/airbytehq/airbyte/pull/56811) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56242](https://github.com/airbytehq/airbyte/pull/56242) | Update dependencies |
| 0.0.15 | 2025-03-09 | [55645](https://github.com/airbytehq/airbyte/pull/55645) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55124](https://github.com/airbytehq/airbyte/pull/55124) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54462](https://github.com/airbytehq/airbyte/pull/54462) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54086](https://github.com/airbytehq/airbyte/pull/54086) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53555](https://github.com/airbytehq/airbyte/pull/53555) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53047](https://github.com/airbytehq/airbyte/pull/53047) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52445](https://github.com/airbytehq/airbyte/pull/52445) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51960](https://github.com/airbytehq/airbyte/pull/51960) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51395](https://github.com/airbytehq/airbyte/pull/51395) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50798](https://github.com/airbytehq/airbyte/pull/50798) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50314](https://github.com/airbytehq/airbyte/pull/50314) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49767](https://github.com/airbytehq/airbyte/pull/49767) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49411](https://github.com/airbytehq/airbyte/pull/49411) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47475](https://github.com/airbytehq/airbyte/pull/47475) | Update dependencies |
| 0.0.1 | 2024-09-23 | [45851](https://github.com/airbytehq/airbyte/pull/45851) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
