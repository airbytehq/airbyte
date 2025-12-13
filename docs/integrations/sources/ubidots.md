# Ubidots
The Ubidots Connector facilitates easy integration with the Ubidots IoT platform, enabling users to fetch, sync, and analyze real-time sensor data. This connector helps streamline IoT workflows by connecting Ubidots with other tools for seamless data processing and insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use for authentication. Obtain it from your Ubidots account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| devices | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| dashboards | id | DefaultPaginator | ✅ |  ❌  |
| variables | id | DefaultPaginator | ✅ |  ❌  |
| device_groups | id | DefaultPaginator | ✅ |  ❌  |
| device_types | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70766](https://github.com/airbytehq/airbyte/pull/70766) | Update dependencies |
| 0.0.42 | 2025-11-25 | [69856](https://github.com/airbytehq/airbyte/pull/69856) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69658](https://github.com/airbytehq/airbyte/pull/69658) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68913](https://github.com/airbytehq/airbyte/pull/68913) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68532](https://github.com/airbytehq/airbyte/pull/68532) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67883](https://github.com/airbytehq/airbyte/pull/67883) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67501](https://github.com/airbytehq/airbyte/pull/67501) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66833](https://github.com/airbytehq/airbyte/pull/66833) | Update dependencies |
| 0.0.35 | 2025-09-23 | [66602](https://github.com/airbytehq/airbyte/pull/66602) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65719](https://github.com/airbytehq/airbyte/pull/65719) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65423](https://github.com/airbytehq/airbyte/pull/65423) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64805](https://github.com/airbytehq/airbyte/pull/64805) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64334](https://github.com/airbytehq/airbyte/pull/64334) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64054](https://github.com/airbytehq/airbyte/pull/64054) | Update dependencies |
| 0.0.29 | 2025-07-20 | [63656](https://github.com/airbytehq/airbyte/pull/63656) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63175](https://github.com/airbytehq/airbyte/pull/63175) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62749](https://github.com/airbytehq/airbyte/pull/62749) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62234](https://github.com/airbytehq/airbyte/pull/62234) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61757](https://github.com/airbytehq/airbyte/pull/61757) | Update dependencies |
| 0.0.24 | 2025-06-15 | [61232](https://github.com/airbytehq/airbyte/pull/61232) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60774](https://github.com/airbytehq/airbyte/pull/60774) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59929](https://github.com/airbytehq/airbyte/pull/59929) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59032](https://github.com/airbytehq/airbyte/pull/59032) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58543](https://github.com/airbytehq/airbyte/pull/58543) | Update dependencies |
| 0.0.19 | 2025-04-13 | [58058](https://github.com/airbytehq/airbyte/pull/58058) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57464](https://github.com/airbytehq/airbyte/pull/57464) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56855](https://github.com/airbytehq/airbyte/pull/56855) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56282](https://github.com/airbytehq/airbyte/pull/56282) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55584](https://github.com/airbytehq/airbyte/pull/55584) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55097](https://github.com/airbytehq/airbyte/pull/55097) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54488](https://github.com/airbytehq/airbyte/pull/54488) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54081](https://github.com/airbytehq/airbyte/pull/54081) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53541](https://github.com/airbytehq/airbyte/pull/53541) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53064](https://github.com/airbytehq/airbyte/pull/53064) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52454](https://github.com/airbytehq/airbyte/pull/52454) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51979](https://github.com/airbytehq/airbyte/pull/51979) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51449](https://github.com/airbytehq/airbyte/pull/51449) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50806](https://github.com/airbytehq/airbyte/pull/50806) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50334](https://github.com/airbytehq/airbyte/pull/50334) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49758](https://github.com/airbytehq/airbyte/pull/49758) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49388](https://github.com/airbytehq/airbyte/pull/49388) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49127](https://github.com/airbytehq/airbyte/pull/49127) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-24 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
