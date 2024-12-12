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
| 0.0.2 | 2024-12-11 | [48988](https://github.com/airbytehq/airbyte/pull/48988) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
