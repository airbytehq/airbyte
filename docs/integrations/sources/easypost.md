# Easypost
This directory contains the manifest-only connector for [`source-easypost`](https://www.easypost.com/).

## Documentation reference:
- Visit [`https://docs.easypost.com/docs/addresses`](https://docs.easypost.com/docs/addresses) for API documentation

## Authentication setup
`EasyPost` uses api key authentication routed as Basic Http, Visit `https://docs.easypost.com/docs/authentication` for getting your api keys.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | API Key. The API Key from your easypost settings |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| batches | id | DefaultPaginator | ✅ |  ✅  |
| addresses | id | DefaultPaginator | ✅ |  ❌  |
| trackers | id | DefaultPaginator | ✅ |  ✅  |
| metadata_carriers | name | No pagination | ✅ |  ❌  |
| end_shippers | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ✅  |
| users_children | id | DefaultPaginator | ✅ |  ✅  |
| carrier_accounts | id | DefaultPaginator | ✅ |  ✅  |
| api_keys | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.39 | 2025-12-09 | [70602](https://github.com/airbytehq/airbyte/pull/70602) | Update dependencies |
| 0.0.38 | 2025-11-25 | [70174](https://github.com/airbytehq/airbyte/pull/70174) | Update dependencies |
| 0.0.37 | 2025-11-18 | [69388](https://github.com/airbytehq/airbyte/pull/69388) | Update dependencies |
| 0.0.36 | 2025-10-29 | [68714](https://github.com/airbytehq/airbyte/pull/68714) | Update dependencies |
| 0.0.35 | 2025-10-21 | [68552](https://github.com/airbytehq/airbyte/pull/68552) | Update dependencies |
| 0.0.34 | 2025-10-14 | [67773](https://github.com/airbytehq/airbyte/pull/67773) | Update dependencies |
| 0.0.33 | 2025-10-07 | [67275](https://github.com/airbytehq/airbyte/pull/67275) | Update dependencies |
| 0.0.32 | 2025-09-30 | [66284](https://github.com/airbytehq/airbyte/pull/66284) | Update dependencies |
| 0.0.31 | 2025-09-09 | [65809](https://github.com/airbytehq/airbyte/pull/65809) | Update dependencies |
| 0.0.30 | 2025-08-23 | [65259](https://github.com/airbytehq/airbyte/pull/65259) | Update dependencies |
| 0.0.29 | 2025-08-09 | [64685](https://github.com/airbytehq/airbyte/pull/64685) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63998](https://github.com/airbytehq/airbyte/pull/63998) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63549](https://github.com/airbytehq/airbyte/pull/63549) | Update dependencies |
| 0.0.26 | 2025-07-12 | [62995](https://github.com/airbytehq/airbyte/pull/62995) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62793](https://github.com/airbytehq/airbyte/pull/62793) | Update dependencies |
| 0.0.24 | 2025-06-28 | [62341](https://github.com/airbytehq/airbyte/pull/62341) | Update dependencies |
| 0.0.23 | 2025-06-22 | [61993](https://github.com/airbytehq/airbyte/pull/61993) | Update dependencies |
| 0.0.22 | 2025-06-14 | [60400](https://github.com/airbytehq/airbyte/pull/60400) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59933](https://github.com/airbytehq/airbyte/pull/59933) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59436](https://github.com/airbytehq/airbyte/pull/59436) | Update dependencies |
| 0.0.19 | 2025-04-26 | [57814](https://github.com/airbytehq/airbyte/pull/57814) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57280](https://github.com/airbytehq/airbyte/pull/57280) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56498](https://github.com/airbytehq/airbyte/pull/56498) | Update dependencies |
| 0.0.16 | 2025-03-22 | [55928](https://github.com/airbytehq/airbyte/pull/55928) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55321](https://github.com/airbytehq/airbyte/pull/55321) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54949](https://github.com/airbytehq/airbyte/pull/54949) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54373](https://github.com/airbytehq/airbyte/pull/54373) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53776](https://github.com/airbytehq/airbyte/pull/53776) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53358](https://github.com/airbytehq/airbyte/pull/53358) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52825](https://github.com/airbytehq/airbyte/pull/52825) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52363](https://github.com/airbytehq/airbyte/pull/52363) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51661](https://github.com/airbytehq/airbyte/pull/51661) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51082](https://github.com/airbytehq/airbyte/pull/51082) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50573](https://github.com/airbytehq/airbyte/pull/50573) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50036](https://github.com/airbytehq/airbyte/pull/50036) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49511](https://github.com/airbytehq/airbyte/pull/49511) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49184](https://github.com/airbytehq/airbyte/pull/49184) | Update dependencies |
| 0.0.2 | 2024-11-04 | [47654](https://github.com/airbytehq/airbyte/pull/47654) | Update dependencies |
| 0.0.1 | 2024-10-01 | [46287](https://github.com/airbytehq/airbyte/pull/46287) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
