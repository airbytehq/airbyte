# OpenAQ
The OpenAQ API provides open access to global air quality data.
This connector enables you to fetch data from all the streams listed on their website such as Locations , Sensors , Measurements and much more.

Docs : https://docs.openaq.org/using-the-api/quick-start

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `country_ids` | `array` | Countries. The list of IDs of countries (comma separated) you need the data for, check more: https://docs.openaq.org/resources/countries |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| instruments | id | DefaultPaginator | ✅ |  ❌  |
| manufacturers | id | DefaultPaginator | ✅ |  ❌  |
| manufacturer_instruments | id | No pagination | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| licenses |  | DefaultPaginator | ✅ |  ❌  |
| license_instrument | id | No pagination | ✅ |  ❌  |
| parameters | id | DefaultPaginator | ✅ |  ❌  |
| countries | id | DefaultPaginator | ✅ |  ❌  |
| latest_parameters |  | No pagination | ✅ |  ❌  |
| sensors | id | DefaultPaginator | ✅ |  ❌  |
| providers | id | DefaultPaginator | ✅ |  ❌  |
| owners | id | DefaultPaginator | ✅ |  ❌  |
| location_latest_measure |  | No pagination | ✅ |  ❌  |
| sensor_measurements |  | DefaultPaginator | ✅ |  ❌  |
| measurements_daily |  | DefaultPaginator | ✅ |  ❌  |
| measurements_yearly |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-06 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
