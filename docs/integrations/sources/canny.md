# Canny
A manifest only source for Canny. https://canny.io/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. You can find your secret API key in Your Canny Subdomain &gt; Settings &gt; API |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| boards | id | No pagination | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| changelog_entries | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| posts | id | DefaultPaginator | ✅ |  ❌  |
| status_changes | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| votes | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|---------|------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 0.0.39 | 2025-12-09 | [70664](https://github.com/airbytehq/airbyte/pull/70664) | Update dependencies |
| 0.0.38 | 2025-11-25 | [69944](https://github.com/airbytehq/airbyte/pull/69944) | Update dependencies |
| 0.0.37 | 2025-11-18 | [69459](https://github.com/airbytehq/airbyte/pull/69459) | Update dependencies |
| 0.0.36 | 2025-10-29 | [68740](https://github.com/airbytehq/airbyte/pull/68740) | Update dependencies |
| 0.0.35 | 2025-10-21 | [68225](https://github.com/airbytehq/airbyte/pull/68225) | Update dependencies |
| 0.0.34 | 2025-10-14 | [67826](https://github.com/airbytehq/airbyte/pull/67826) | Update dependencies |
| 0.0.33 | 2025-10-07 | [67210](https://github.com/airbytehq/airbyte/pull/67210) | Update dependencies |
| 0.0.32 | 2025-09-30 | [66326](https://github.com/airbytehq/airbyte/pull/66326) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65310](https://github.com/airbytehq/airbyte/pull/65310) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64662](https://github.com/airbytehq/airbyte/pull/64662) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63803](https://github.com/airbytehq/airbyte/pull/63803) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63035](https://github.com/airbytehq/airbyte/pull/63035) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62529](https://github.com/airbytehq/airbyte/pull/62529) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62137](https://github.com/airbytehq/airbyte/pull/62137) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61450](https://github.com/airbytehq/airbyte/pull/61450) | Update dependencies |
| 0.0.24 | 2025-05-24 | [59838](https://github.com/airbytehq/airbyte/pull/59838) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59313](https://github.com/airbytehq/airbyte/pull/59313) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58706](https://github.com/airbytehq/airbyte/pull/58706) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58253](https://github.com/airbytehq/airbyte/pull/58253) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57653](https://github.com/airbytehq/airbyte/pull/57653) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57188](https://github.com/airbytehq/airbyte/pull/57188) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56580](https://github.com/airbytehq/airbyte/pull/56580) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56093](https://github.com/airbytehq/airbyte/pull/56093) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55398](https://github.com/airbytehq/airbyte/pull/55398) | Update dependencies |
| 0.0.15 | 2025-03-01 | [54867](https://github.com/airbytehq/airbyte/pull/54867) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54212](https://github.com/airbytehq/airbyte/pull/54212) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53884](https://github.com/airbytehq/airbyte/pull/53884) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53406](https://github.com/airbytehq/airbyte/pull/53406) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52902](https://github.com/airbytehq/airbyte/pull/52902) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52153](https://github.com/airbytehq/airbyte/pull/52153) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51765](https://github.com/airbytehq/airbyte/pull/51765) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51237](https://github.com/airbytehq/airbyte/pull/51237) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50489](https://github.com/airbytehq/airbyte/pull/50489) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50171](https://github.com/airbytehq/airbyte/pull/50171) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49574](https://github.com/airbytehq/airbyte/pull/49574) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49013](https://github.com/airbytehq/airbyte/pull/49013) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48235](https://github.com/airbytehq/airbyte/pull/48235) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47727](https://github.com/airbytehq/airbyte/pull/47727) | Update dependencies |
| 0.0.1 | 2024-09-15 | [45588](https://github.com/airbytehq/airbyte/pull/45588) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
