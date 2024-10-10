# Statistics Netherlands CBS
Dataset Open API: https://dataderden.cbs.nl/ODataApi/
Dataset Selection Website: https://opendata.cbs.nl/statline/portal.html?_la=en&amp;_catalog=CBS (Select a theme and click on API on left bar to find base number for dataset)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_number` | `array` | Base number of dataset. Base number found at end of open data API. Refer `https://dataderden.cbs.nl/ODataApi/` | [48002NED, 48004NED] |
| `start_date` | `string` | Start date.  |  |

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
| 0.0.1 | 2024-10-10 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
