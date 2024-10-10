# Statistics Netherlands CBS

## Overview
This connector is for fetching open statistical dataset of netherlands, the [CBS Opendata website](https://opendata.cbs.nl) provides dataset within several themes, Visit `https://opendata.cbs.nl/statline/portal.html?_la=en&amp;_catalog=CBS`, select a theme and click of API tab in left bar to find the link with dataset number which could be given as config for this connector

Example Open API Dataset : https://dataderden.cbs.nl/ODataApi/
Dataset Selection Website: https://opendata.cbs.nl/statline/portal.html?_la=en&amp;_catalog=CBS (Select a theme and click on API on left bar to find base number for dataset)


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_number` | `array` | Base number of dataset. Base number found at end of open data API. Refer `https://dataderden.cbs.nl/ODataApi/` | [48004NED] |
| `start_date` | `string` | Start date.  |  |
| `base_origin` | `string` | Base origin of the URL, Example: `dataderden.cbs.nl`, `opendata.cbs.nl/`.  | dataderden |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| open_data_base | id | No pagination | ✅ |  ❌  |
| table_infos | Identifier | No pagination | ✅ |  ✅  |
| untyped_data_set | uuid | No pagination | ✅ |  ❌  |
| typed_data_set | uuid | No pagination | ✅ |  ❌  |
| data_properties | uuid | No pagination | ✅ |  ❌  |
| category_groups | uuid | No pagination | ✅ |  ❌  |
| perioden | uuid | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-10 | [46633](https://github.com/airbytehq/airbyte/issues/46633) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
