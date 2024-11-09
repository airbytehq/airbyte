# USDA FAS
This provides access to publicly available agricultural commodity data from the Export Sales Report (ESR), Global Agricultural Trade System (GATS), and Production, Supply &amp; Distribution (PSD) databases.
Docs : https://apps.fas.usda.gov/opendatawebV2/#/home

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `market_year` | `integer` | Market Year.  | 2023 |
| `country_codes` | `array` | ESR Country Codes.  |  |
| `commodities_codes` | `array` | ESR Commodities Codes.  |  |
| `gats_reporter_codes` | `array` | GATS Reporter Codes.  |  |
| `psd_commodities_codes` | `array` | PSD Commodities Codes.  |  |
| `psd_country_codes` | `array` | PSD Country Codes.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| gats_commodity_import_data |  | No pagination | ✅ |  ❌  |
| gats_commodity_export_data |  | No pagination | ✅ |  ❌  |
| esr_export_data |  | No pagination | ✅ |  ❌  |
| psd_forcecastnumber |  | No pagination | ✅ |  ❌  |
| psd_forecastnumber_commodity |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
