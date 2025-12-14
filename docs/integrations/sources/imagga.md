# Imagga
Website: https://imagga.com/
API Reference: https://docs.imagga.com/#introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Imagga API key, available in your Imagga dashboard. Could be found at `https://imagga.com/profile/dashboard` |  |
| `api_secret` | `string` | API Secret. Your Imagga API secret, available in your Imagga dashboard. Could be found at `https://imagga.com/profile/dashboard` |  |
| `img_for_detection` | `string` | Image URL for detection endpoints. An image for detection endpoints | https://imagga.com/static/images/categorization/child-476506_640.jpg |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| categorizers | id | DefaultPaginator | ❌ |  ❌  |
| croppings | uuid | DefaultPaginator | ❌ |  ❌  |
| colors | uuid | DefaultPaginator | ❌ |  ❌  |
| faces_detections | uuid | DefaultPaginator | ❌ |  ❌  |
| text | uuid | DefaultPaginator | ❌ |  ❌  |
| usage | uuid | DefaultPaginator | ❌ |  ❌  |
| barcodes | uuid | DefaultPaginator | ❌ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.26 | 2025-12-09 | [70463](https://github.com/airbytehq/airbyte/pull/70463) | Update dependencies |
| 0.0.25 | 2025-11-25 | [70163](https://github.com/airbytehq/airbyte/pull/70163) | Update dependencies |
| 0.0.24 | 2025-11-18 | [69514](https://github.com/airbytehq/airbyte/pull/69514) | Update dependencies |
| 0.0.23 | 2025-10-29 | [68775](https://github.com/airbytehq/airbyte/pull/68775) | Update dependencies |
| 0.0.22 | 2025-10-21 | [68504](https://github.com/airbytehq/airbyte/pull/68504) | Update dependencies |
| 0.0.21 | 2025-10-14 | [67903](https://github.com/airbytehq/airbyte/pull/67903) | Update dependencies |
| 0.0.20 | 2025-10-07 | [67410](https://github.com/airbytehq/airbyte/pull/67410) | Update dependencies |
| 0.0.19 | 2025-09-30 | [66803](https://github.com/airbytehq/airbyte/pull/66803) | Update dependencies |
| 0.0.18 | 2025-09-09 | [65899](https://github.com/airbytehq/airbyte/pull/65899) | Update dependencies |
| 0.0.17 | 2025-08-23 | [65360](https://github.com/airbytehq/airbyte/pull/65360) | Update dependencies |
| 0.0.16 | 2025-08-09 | [64595](https://github.com/airbytehq/airbyte/pull/64595) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64177](https://github.com/airbytehq/airbyte/pull/64177) | Update dependencies |
| 0.0.14 | 2025-07-26 | [63879](https://github.com/airbytehq/airbyte/pull/63879) | Update dependencies |
| 0.0.13 | 2025-07-19 | [63527](https://github.com/airbytehq/airbyte/pull/63527) | Update dependencies |
| 0.0.12 | 2025-07-12 | [63151](https://github.com/airbytehq/airbyte/pull/63151) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62585](https://github.com/airbytehq/airbyte/pull/62585) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62171](https://github.com/airbytehq/airbyte/pull/62171) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61864](https://github.com/airbytehq/airbyte/pull/61864) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61094](https://github.com/airbytehq/airbyte/pull/61094) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60667](https://github.com/airbytehq/airbyte/pull/60667) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59848](https://github.com/airbytehq/airbyte/pull/59848) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59293](https://github.com/airbytehq/airbyte/pull/59293) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58809](https://github.com/airbytehq/airbyte/pull/58809) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58222](https://github.com/airbytehq/airbyte/pull/58222) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57722](https://github.com/airbytehq/airbyte/pull/57722) | Update dependencies |
| 0.0.1 | 2025-04-05 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
