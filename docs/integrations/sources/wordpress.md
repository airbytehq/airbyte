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
| 0.0.5 | 2024-12-28 | [50763](https://github.com/airbytehq/airbyte/pull/50763) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50361](https://github.com/airbytehq/airbyte/pull/50361) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49743](https://github.com/airbytehq/airbyte/pull/49743) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49433](https://github.com/airbytehq/airbyte/pull/49433) | Update dependencies |
| 0.0.1   | 2024-10-21 | 46378        | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
