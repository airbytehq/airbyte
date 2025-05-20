# Wordpress

The WordPress connector enables seamless data synchronization between your WordPress site and various destinations. With this connector, you can effortlessly extract and integrate blog posts, pages, comments, and other WordPress data into your preferred analytics or storage platform, enabling streamlined data analysis and reporting.

## Configuration

| Input        | Type     | Description                                                                                    | Default Value |
| ------------ | -------- | ---------------------------------------------------------------------------------------------- | ------------- |
| `domain`     | `string` | Domain. The domain of the WordPress site. Example: my-wordpress-website.host.com               |               |
| `password`   | `string` | Placeholder Password. Placeholder for basic HTTP auth password - should be set to empty string | x             |
| `username`   | `string` | Placeholder Username. Placeholder for basic HTTP auth username - should be set to empty string | x             |
| `start_date` | `string` | Start Date. Minimal Date to Retrieve Records when stream allow incremental.                    |               |

## Streams

| Stream Name    | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
| -------------- | ----------- | ---------------- | ------------------ | -------------------- |
| users          | id          | DefaultPaginator | ✅                 | ❌                   |
| posts          | id          | DefaultPaginator | ✅                 | ❌                   |
| categories     | id          | DefaultPaginator | ✅                 | ❌                   |
| plugins        | plugin      | No pagination    | ✅                 | ❌                   |
| editor_blocks  | id          | DefaultPaginator | ✅                 | ✅                   |
| comments       | id          | DefaultPaginator | ✅                 | ✅                   |
| pages          | id          | DefaultPaginator | ✅                 | ✅                   |
| tags           | id          | DefaultPaginator | ✅                 | ❌                   |
| page_revisions | id          | DefaultPaginator | ✅                 | ❌                   |
| media          | id          | DefaultPaginator | ✅                 | ✅                   |
| taxonomies     | category    | No pagination    | ✅                 | ❌                   |
| types          |             | No pagination    | ✅                 | ❌                   |
| themes         | stylesheet  | No pagination    | ✅                 | ❌                   |
| statuses       |             | No pagination    | ✅                 | ❌                   |
| settings       |             | No pagination    | ✅                 | ❌                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                               |
| ------- | ---------- | ------------ | ------------------------------------------------------------------------------------- |
| 0.0.22 | 2025-05-10 | [60006](https://github.com/airbytehq/airbyte/pull/60006) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59556](https://github.com/airbytehq/airbyte/pull/59556) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58946](https://github.com/airbytehq/airbyte/pull/58946) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58568](https://github.com/airbytehq/airbyte/pull/58568) | Update dependencies |
| 0.0.18 | 2025-04-13 | [58050](https://github.com/airbytehq/airbyte/pull/58050) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57402](https://github.com/airbytehq/airbyte/pull/57402) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56901](https://github.com/airbytehq/airbyte/pull/56901) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56297](https://github.com/airbytehq/airbyte/pull/56297) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55593](https://github.com/airbytehq/airbyte/pull/55593) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55140](https://github.com/airbytehq/airbyte/pull/55140) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54494](https://github.com/airbytehq/airbyte/pull/54494) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54027](https://github.com/airbytehq/airbyte/pull/54027) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53564](https://github.com/airbytehq/airbyte/pull/53564) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53044](https://github.com/airbytehq/airbyte/pull/53044) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52424](https://github.com/airbytehq/airbyte/pull/52424) | Update dependencies |
| 0.0.7 | 2025-01-18 | [52008](https://github.com/airbytehq/airbyte/pull/52008) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51432](https://github.com/airbytehq/airbyte/pull/51432) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50763](https://github.com/airbytehq/airbyte/pull/50763) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50361](https://github.com/airbytehq/airbyte/pull/50361) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49743](https://github.com/airbytehq/airbyte/pull/49743) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49433](https://github.com/airbytehq/airbyte/pull/49433) | Update dependencies |
| 0.0.1   | 2024-10-21 | 46378        | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
