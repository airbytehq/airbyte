# Nutshell
Nutshell is a CRM tool.
Using this connector we can extract data from various streams such as contacts , events , products and pipelines.
[API Docs](https://developers.nutshell.com/docs/getting-started)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | API Token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| accounts_list_items | id | No pagination | ✅ |  ❌  |
| account_types | id | No pagination | ✅ |  ❌  |
| industries | id | No pagination | ✅ |  ❌  |
| activities | id | DefaultPaginator | ✅ |  ❌  |
| activity_types | id | No pagination | ✅ |  ❌  |
| audiences | id | No pagination | ✅ |  ❌  |
| competitors | id | No pagination | ✅ |  ❌  |
| competitor_maps | id | No pagination | ✅ |  ❌  |
| leads_custom_fields | id | No pagination | ✅ |  ❌  |
| leads_list_items | id | No pagination | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| leads_report | id | No pagination | ✅ |  ❌  |
| contacts_custom_fields | id | No pagination | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| contacts_list_items | id | No pagination | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| filters | id | No pagination | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| products | id | No pagination | ✅ |  ❌  |
| lead_products | id | No pagination | ✅ |  ❌  |
| sources | id | No pagination | ✅ |  ❌  |
| stages | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70596](https://github.com/airbytehq/airbyte/pull/70596) | Update dependencies |
| 0.0.42 | 2025-11-25 | [69854](https://github.com/airbytehq/airbyte/pull/69854) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69415](https://github.com/airbytehq/airbyte/pull/69415) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68742](https://github.com/airbytehq/airbyte/pull/68742) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68378](https://github.com/airbytehq/airbyte/pull/68378) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67725](https://github.com/airbytehq/airbyte/pull/67725) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67421](https://github.com/airbytehq/airbyte/pull/67421) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66923](https://github.com/airbytehq/airbyte/pull/66923) | Update dependencies |
| 0.0.35 | 2025-09-23 | [66615](https://github.com/airbytehq/airbyte/pull/66615) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65830](https://github.com/airbytehq/airbyte/pull/65830) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65169](https://github.com/airbytehq/airbyte/pull/65169) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64676](https://github.com/airbytehq/airbyte/pull/64676) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64260](https://github.com/airbytehq/airbyte/pull/64260) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63899](https://github.com/airbytehq/airbyte/pull/63899) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63438](https://github.com/airbytehq/airbyte/pull/63438) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63252](https://github.com/airbytehq/airbyte/pull/63252) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62660](https://github.com/airbytehq/airbyte/pull/62660) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62345](https://github.com/airbytehq/airbyte/pull/62345) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61893](https://github.com/airbytehq/airbyte/pull/61893) | Update dependencies |
| 0.0.24 | 2025-06-14 | [60473](https://github.com/airbytehq/airbyte/pull/60473) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60189](https://github.com/airbytehq/airbyte/pull/60189) | Update dependencies |
| 0.0.22 | 2025-05-03 | [59479](https://github.com/airbytehq/airbyte/pull/59479) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59071](https://github.com/airbytehq/airbyte/pull/59071) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58476](https://github.com/airbytehq/airbyte/pull/58476) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57885](https://github.com/airbytehq/airbyte/pull/57885) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57353](https://github.com/airbytehq/airbyte/pull/57353) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56740](https://github.com/airbytehq/airbyte/pull/56740) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56187](https://github.com/airbytehq/airbyte/pull/56187) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55549](https://github.com/airbytehq/airbyte/pull/55549) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54828](https://github.com/airbytehq/airbyte/pull/54828) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54549](https://github.com/airbytehq/airbyte/pull/54549) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53959](https://github.com/airbytehq/airbyte/pull/53959) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53254](https://github.com/airbytehq/airbyte/pull/53254) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52757](https://github.com/airbytehq/airbyte/pull/52757) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52274](https://github.com/airbytehq/airbyte/pull/52274) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51825](https://github.com/airbytehq/airbyte/pull/51825) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51160](https://github.com/airbytehq/airbyte/pull/51160) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50615](https://github.com/airbytehq/airbyte/pull/50615) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50130](https://github.com/airbytehq/airbyte/pull/50130) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49641](https://github.com/airbytehq/airbyte/pull/49641) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49228](https://github.com/airbytehq/airbyte/pull/49228) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48988](https://github.com/airbytehq/airbyte/pull/48988) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
