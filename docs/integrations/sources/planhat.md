# Planhat

This source can sync data for the [general Planhat API](https://docs.planhat.com/).

This Source is capable of syncing the following core Streams:

- [companies](https://docs.planhat.com/#companies)
- [conversations](https://docs.planhat.com/#conversations)
- [custom_fields](https://docs.planhat.com/#custom_fields)
- [endusers](https://docs.planhat.com/#endusers)
- [invoices](https://docs.planhat.com/#invoices)
- [issues](https://docs.planhat.com/#issues)
- [licenses](https://docs.planhat.com/#licenses)
- [nps](https://docs.planhat.com/#nps)
- [opportunities](https://docs.planhat.com/#opportunities)
- [objectives](https://docs.planhat.com/#objectives)
- [sales](https://docs.planhat.com/#sales)
- [tasks](https://docs.planhat.com/#tasks)
- [tickets](https://docs.planhat.com/#tickets)
- [users](https://docs.planhat.com/#users)

## Configuration

| Input       | Type     | Description                                                                          | Default Value |
| ----------- | -------- | ------------------------------------------------------------------------------------ | ------------- |
| `api_token` | `string` | API Token. Your Planhat [API Access Token](https://docs.planhat.com/#authentication) |               |

## Streams

| Stream Name     | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
| --------------- | ----------- | ---------------- | ------------------ | -------------------- |
| `assets`        | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `churn`         | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `companies`     | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `conversations` | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `custom_fields` | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `endusers`      | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `invoices`      | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `issues`        | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `licenses`      | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `nps`           | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `workflows`     | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `opportunities` | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `objectives`    | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `sales`         | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `tasks`         | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `tickets`       | `_id`       | DefaultPaginator | ✅                 | ❌                   |
| `users`         | `_id`       | DefaultPaginator | ✅                 | ❌                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                              |
| ------- | ---------- | ------------ | ---------------------------------------------------- |
| 0.0.2 | 2024-09-30 | [46271](https://github.com/airbytehq/airbyte/pull/46271) | Documentation update |
| 0.0.1   | 2024-08-22 |              | Initial release by natikgadzhi via Connector Builder |

</details>
