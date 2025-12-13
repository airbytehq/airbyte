# Coassemble
Coassemble is an online training tool that connects people with the information they need - anytime, anyplace.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_token` | `string` | User Token.  |  |
| `user_id` | `string` | User ID.  |  |

See the [Coassemble API docs](https://developers.coassemble.com/get-started) for more information to get started and generate API credentials.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| courses | id | DefaultPaginator | ✅ |  ❌  |
| screen_types | - | NoPaginator | ✅ |  ❌  |
| trackings | - | DefaultPaginator | ✅ |  ❌  |

⚠️⚠️ Note: The `screen_types` and `trackings` streams are **Available on request only** as per the [API docs](https://developers.coassemble.com/get-started). Hence, enabling them without having them enabled on the API side would result in errors. ⚠️⚠️

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.41 | 2025-12-09 | [70653](https://github.com/airbytehq/airbyte/pull/70653) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69942](https://github.com/airbytehq/airbyte/pull/69942) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69612](https://github.com/airbytehq/airbyte/pull/69612) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68898](https://github.com/airbytehq/airbyte/pull/68898) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68530](https://github.com/airbytehq/airbyte/pull/68530) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68059](https://github.com/airbytehq/airbyte/pull/68059) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67182](https://github.com/airbytehq/airbyte/pull/67182) | Update dependencies |
| 0.0.34 | 2025-09-30 | [65868](https://github.com/airbytehq/airbyte/pull/65868) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65251](https://github.com/airbytehq/airbyte/pull/65251) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64751](https://github.com/airbytehq/airbyte/pull/64751) | Update dependencies |
| 0.0.31 | 2025-08-02 | [63943](https://github.com/airbytehq/airbyte/pull/63943) | Update dependencies |
| 0.0.30 | 2025-07-19 | [63547](https://github.com/airbytehq/airbyte/pull/63547) | Update dependencies |
| 0.0.29 | 2025-07-12 | [62958](https://github.com/airbytehq/airbyte/pull/62958) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62788](https://github.com/airbytehq/airbyte/pull/62788) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62352](https://github.com/airbytehq/airbyte/pull/62352) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61980](https://github.com/airbytehq/airbyte/pull/61980) | Update dependencies |
| 0.0.25 | 2025-06-14 | [60409](https://github.com/airbytehq/airbyte/pull/60409) | Update dependencies |
| 0.0.24 | 2025-05-10 | [60029](https://github.com/airbytehq/airbyte/pull/60029) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59382](https://github.com/airbytehq/airbyte/pull/59382) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58902](https://github.com/airbytehq/airbyte/pull/58902) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58300](https://github.com/airbytehq/airbyte/pull/58300) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57793](https://github.com/airbytehq/airbyte/pull/57793) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57279](https://github.com/airbytehq/airbyte/pull/57279) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56530](https://github.com/airbytehq/airbyte/pull/56530) | Update dependencies |
| 0.0.17 | 2025-03-22 | [55977](https://github.com/airbytehq/airbyte/pull/55977) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55333](https://github.com/airbytehq/airbyte/pull/55333) | Update dependencies |
| 0.0.15 | 2025-03-01 | [54940](https://github.com/airbytehq/airbyte/pull/54940) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54419](https://github.com/airbytehq/airbyte/pull/54419) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53757](https://github.com/airbytehq/airbyte/pull/53757) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53331](https://github.com/airbytehq/airbyte/pull/53331) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52795](https://github.com/airbytehq/airbyte/pull/52795) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52339](https://github.com/airbytehq/airbyte/pull/52339) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51699](https://github.com/airbytehq/airbyte/pull/51699) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51123](https://github.com/airbytehq/airbyte/pull/51123) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50570](https://github.com/airbytehq/airbyte/pull/50570) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50025](https://github.com/airbytehq/airbyte/pull/50025) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49483](https://github.com/airbytehq/airbyte/pull/49483) | Update dependencies |
| 0.0.4 | 2024-12-12 | [48926](https://github.com/airbytehq/airbyte/pull/48926) | Update dependencies |
| 0.0.3 | 2024-11-04 | [47865](https://github.com/airbytehq/airbyte/pull/47865) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47526](https://github.com/airbytehq/airbyte/pull/47526) | Update dependencies |
| 0.0.1 | 2024-09-19 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
