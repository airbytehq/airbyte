# USDA FAS
This provides access to publicly available agricultural commodity data from the Export Sales Report (ESR), Global Agricultural Trade System (GATS), and Production, Supply &amp; Distribution (PSD) databases.
Docs : https://apps.fas.usda.gov/opendatawebV2/#/home

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `market_year` | `integer` | Market Year.  | 2023 |
| `year` | `integer` | Year.  | 2023 |
| `month` | `integer` | Month.  | 01 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| esr_regions | regionId | No pagination | ✅ |  ❌  |
| esr_countries | countryCode | No pagination | ✅ |  ❌  |
| esr_commodities | commodityCode | No pagination | ✅ |  ❌  |
| esr_unitsofmeasure | unitId | No pagination | ✅ |  ❌  |
| esr_datareleasedates |  | No pagination | ✅ |  ❌  |
| gats_export_data_releasedates |  | No pagination | ✅ |  ❌  |
| gats_import_data_releasedates |  | No pagination | ✅ |  ❌  |
| gats_untrade_data_exports_data_releasedates |  | No pagination | ✅ |  ❌  |
| gats_untrade_data_imports_data_releasedates |  | No pagination | ✅ |  ❌  |
| gats_regions | regionCode | No pagination | ✅ |  ❌  |
| gats_countries | countryCode | No pagination | ✅ |  ❌  |
| gats_commodities |  | No pagination | ✅ |  ❌  |
| gats_hs6commodities | hS6Code | No pagination | ✅ |  ❌  |
| gats_unitsOfMeasure |  | No pagination | ✅ |  ❌  |
| gats_customsdistricts |  | No pagination | ✅ |  ❌  |
| commodity_import_data |  | No pagination | ✅ |  ❌  |
| commodity_export_data |  | No pagination | ✅ |  ❌  |
| psd_regions | regionCode | No pagination | ✅ |  ❌  |
| psd_countries | countryCode | No pagination | ✅ |  ❌  |
| psd_commodities | commodityCode | No pagination | ✅ |  ❌  |
| psd_unitsOfMeasure | unitId | No pagination | ✅ |  ❌  |
| psd_commodityAttributes | attributeId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-01 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
