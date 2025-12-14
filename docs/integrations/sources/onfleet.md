# Onfleet
This is the Onfleet connector that ingests data from the Onfleet API.

Onfleet is the world&#39;s advanced logistics software that delights customers, scale operations, and boost efficiency https://onfleet.com/

In order to use this source you must first create an account on Onfleet. Once logged in, you can find the can create an API keys through the settings menu in the dashboard, by going into the API section.

You can find more information about the API here https://docs.onfleet.com/reference/setup-tutorial

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use for authenticating requests. You can create and manage your API keys in the API section of the Onfleet dashboard. |  |
| `password` | `string` | Placeholder Password. Placeholder for basic HTTP auth password - should be set to empty string | x |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| workers | id | No pagination | ✅ |  ❌  |
| administrators | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| hubs | id | No pagination | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| containers | id | No pagination | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.42 | 2025-12-09 | [70509](https://github.com/airbytehq/airbyte/pull/70509) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70135](https://github.com/airbytehq/airbyte/pull/70135) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69419](https://github.com/airbytehq/airbyte/pull/69419) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68733](https://github.com/airbytehq/airbyte/pull/68733) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68350](https://github.com/airbytehq/airbyte/pull/68350) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67733](https://github.com/airbytehq/airbyte/pull/67733) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67423](https://github.com/airbytehq/airbyte/pull/67423) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66935](https://github.com/airbytehq/airbyte/pull/66935) | Update dependencies |
| 0.0.34 | 2025-09-23 | [66616](https://github.com/airbytehq/airbyte/pull/66616) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65800](https://github.com/airbytehq/airbyte/pull/65800) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65211](https://github.com/airbytehq/airbyte/pull/65211) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64773](https://github.com/airbytehq/airbyte/pull/64773) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64242](https://github.com/airbytehq/airbyte/pull/64242) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63811](https://github.com/airbytehq/airbyte/pull/63811) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63384](https://github.com/airbytehq/airbyte/pull/63384) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63168](https://github.com/airbytehq/airbyte/pull/63168) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62659](https://github.com/airbytehq/airbyte/pull/62659) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62311](https://github.com/airbytehq/airbyte/pull/62311) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61889](https://github.com/airbytehq/airbyte/pull/61889) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61024](https://github.com/airbytehq/airbyte/pull/61024) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60530](https://github.com/airbytehq/airbyte/pull/60530) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60172](https://github.com/airbytehq/airbyte/pull/60172) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59478](https://github.com/airbytehq/airbyte/pull/59478) | Update dependencies |
| 0.0.19 | 2025-04-27 | [59084](https://github.com/airbytehq/airbyte/pull/59084) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58480](https://github.com/airbytehq/airbyte/pull/58480) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57874](https://github.com/airbytehq/airbyte/pull/57874) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57312](https://github.com/airbytehq/airbyte/pull/57312) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56753](https://github.com/airbytehq/airbyte/pull/56753) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56197](https://github.com/airbytehq/airbyte/pull/56197) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55056](https://github.com/airbytehq/airbyte/pull/55056) | Update dependencies |
| 0.0.12 | 2025-02-23 | [54607](https://github.com/airbytehq/airbyte/pull/54607) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53998](https://github.com/airbytehq/airbyte/pull/53998) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53494](https://github.com/airbytehq/airbyte/pull/53494) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53012](https://github.com/airbytehq/airbyte/pull/53012) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52532](https://github.com/airbytehq/airbyte/pull/52532) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51865](https://github.com/airbytehq/airbyte/pull/51865) | Update dependencies |
| 0.0.6 | 2025-01-11 | [50727](https://github.com/airbytehq/airbyte/pull/50727) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50295](https://github.com/airbytehq/airbyte/pull/50295) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49712](https://github.com/airbytehq/airbyte/pull/49712) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49336](https://github.com/airbytehq/airbyte/pull/49336) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49051](https://github.com/airbytehq/airbyte/pull/49051) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-27 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
