# OpenAQ
The OpenAQ API provides open access to global air quality data.
This connector enables you to fetch data from all the streams listed on their website such as Locations , Sensors , Measurements and much more.
Docs : https://docs.openaq.org/using-the-api/quick-start

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Instruments | id | DefaultPaginator | ✅ |  ❌  |
| Instrument |  | No pagination | ✅ |  ❌  |
| Manufacturers | id | DefaultPaginator | ✅ |  ❌  |
| Manufacturer | id | No pagination | ✅ |  ❌  |
| Manufacturer Instruments | id | No pagination | ✅ |  ❌  |
| Locations | id | No pagination | ✅ |  ❌  |
| Location | id | No pagination | ✅ |  ❌  |
| Licenses |  | DefaultPaginator | ✅ |  ❌  |
| License Instrument | id | No pagination | ✅ |  ❌  |
| Parameters | id | DefaultPaginator | ✅ |  ❌  |
| Parameter |  | No pagination | ✅ |  ❌  |
| Countries | id | DefaultPaginator | ✅ |  ❌  |
| Country |  | No pagination | ✅ |  ❌  |
| Latest Parameters |  | No pagination | ✅ |  ❌  |
| Sensors | id | No pagination | ✅ |  ❌  |
| Sensor | id | No pagination | ✅ |  ❌  |
| Providers | id | DefaultPaginator | ✅ |  ❌  |
| Provider | id | No pagination | ✅ |  ❌  |
| Owners | id | DefaultPaginator | ✅ |  ❌  |
| Owner | id | No pagination | ✅ |  ❌  |
| Location’s Latest Measurement |  | No pagination | ✅ |  ❌  |
| Measurements |  | DefaultPaginator | ✅ |  ❌  |
| Measurements Aggregated To Day |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated To Year |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Day to Year |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Days to Month |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Day to Month of Year |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Day to Day Of Week |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hour To Month of Year |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hour To Day Of Week |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hour To Hour of Day |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hour To Year |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hours to Monthly |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated From Hours to Daily |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated To Hour |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated To Daily |  | No pagination | ✅ |  ❌  |
| Measurements Aggregated To Hourly |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-19 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
