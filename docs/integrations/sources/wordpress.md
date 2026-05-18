# WordPress

<HideInUI>

This page contains the setup guide and reference information for the [WordPress](https://wordpress.org/) source connector.

</HideInUI>

## Prerequisites

- A self-hosted WordPress site (WordPress.org) with the [REST API](https://developer.wordpress.org/rest-api/) enabled (default on WordPress 4.7 and later).
- The site's domain name—for example, `my-site.example.com`.

:::note
This connector reads data from the public WordPress REST API. Most read endpoints for posts, pages, comments, categories, tags, and media are accessible without authentication. Endpoints that expose private data—such as plugins, themes, settings, and users with full details—require authentication.
:::

### Authentication

The connector sends HTTP Basic Authentication headers with each request. For public endpoints, you can leave the **Username** and **Password** fields at their default values.

To access authenticated endpoints such as plugins, themes, and settings, provide valid WordPress credentials. WordPress supports [Application Passwords](https://developer.wordpress.org/advanced-administration/security/application-passwords/) (available since WordPress 5.6), which are the recommended method for REST API authentication:

1. In your WordPress admin dashboard, go to **Users > Profile**.
2. Scroll to the **Application Passwords** section.
3. Enter a name for the application (for example, `Airbyte`) and click **Add New Application Password**.
4. Copy the generated password. Use your WordPress username and this application password as the connector credentials.

## Setup guide

1. Enter the **Domain** of your WordPress site without the protocol—for example, `my-site.example.com`.
2. Enter your **Username** and **Password**. Leave the default values if you only need to sync public data.
3. Optionally, set a **Start Date** to limit incremental streams to records modified after that date. Use the format `YYYY-MM-DDTHH:MM:SSZ`—for example, `2024-01-01T00:00:00Z`.
4. Optionally, set a **Lookback Window** (in hours) for incremental streams. This re-fetches the specified number of hours of previously synced data on each sync to guard against data loss. Set to `0` to disable. Duplicates are handled by destination deduplication.

<HideInUI>

## Supported sync modes

The WordPress source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

The connector syncs data from the following [WordPress REST API](https://developer.wordpress.org/rest-api/reference/) endpoints:

| Stream | API Endpoint | Sync Mode | Pagination | Primary Key | Description |
| --- | --- | --- | --- | --- | --- |
| [users](https://developer.wordpress.org/rest-api/reference/users/) | `/wp/v2/users` | Full Refresh | Yes | `id` | Site authors and contributors. |
| [posts](https://developer.wordpress.org/rest-api/reference/posts/) | `/wp/v2/posts` | Full Refresh | Yes | `id` | Blog posts. |
| [categories](https://developer.wordpress.org/rest-api/reference/categories/) | `/wp/v2/categories` | Full Refresh | Yes | `id` | Post categories. |
| [tags](https://developer.wordpress.org/rest-api/reference/tags/) | `/wp/v2/tags` | Full Refresh | Yes | `id` | Post tags. |
| [pages](https://developer.wordpress.org/rest-api/reference/pages/) | `/wp/v2/pages` | Incremental | Yes | `id` | Static pages. Cursor field: `modified`. |
| [page_revisions](https://developer.wordpress.org/rest-api/reference/page-revisions/) | `/wp/v2/pages/{id}/revisions` | Full Refresh | Yes | `id` | Revision history for each page. |
| [comments](https://developer.wordpress.org/rest-api/reference/comments/) | `/wp/v2/comments` | Incremental | Yes | `id` | Comments on posts and pages. Cursor field: `date`. |
| [media](https://developer.wordpress.org/rest-api/reference/media/) | `/wp/v2/media` | Incremental | Yes | `id` | Uploaded images, videos, and other media files. Cursor field: `modified`. |
| [editor_blocks](https://developer.wordpress.org/rest-api/reference/blocks/) | `/wp/v2/blocks` | Incremental | Yes | `id` | Reusable block patterns (synced patterns). Cursor field: `modified`. |
| [plugins](https://developer.wordpress.org/rest-api/reference/plugins/) | `/wp/v2/plugins` | Full Refresh | No | `plugin` | Installed plugins. Requires authentication. |
| [taxonomies](https://developer.wordpress.org/rest-api/reference/taxonomies/) | `/wp/v2/taxonomies` | Full Refresh | No | `category` | Registered taxonomies (for example, categories and tags). |
| [types](https://developer.wordpress.org/rest-api/reference/post-types/) | `/wp/v2/types` | Full Refresh | No | — | Registered post types (for example, post, page, attachment). |
| [themes](https://developer.wordpress.org/rest-api/reference/themes/) | `/wp/v2/themes` | Full Refresh | No | `stylesheet` | Installed themes. Requires authentication. |
| [statuses](https://developer.wordpress.org/rest-api/reference/post-statuses/) | `/wp/v2/statuses` | Full Refresh | No | — | Available post statuses (for example, publish, draft, private). |
| [settings](https://developer.wordpress.org/rest-api/reference/settings/) | `/wp/v2/settings` | Full Refresh | No | — | Site-wide settings such as title, description, and timezone. Requires authentication. |

### Incremental sync details

The `pages`, `media`, and `editor_blocks` streams use the `modified` field as the cursor, tracking records by their last modification time in the site's local timezone. The `comments` stream uses the `date` field.

Because these timestamps use the site's local timezone, clock changes during daylight saving time (DST) transitions can cause non-monotonic timestamps. If this is a concern, configure a **Lookback Window** to re-fetch recent data and prevent gaps.

## Limitations

- **Pagination**: The WordPress REST API limits paginated responses to a maximum of 100 items per page. The connector handles this automatically.
- **Authenticated endpoints**: The `plugins`, `themes`, and `settings` streams require valid credentials. If the connector is configured without authentication, these streams return errors or empty results.
- **WordPress.com hosted sites**: This connector is designed for the self-hosted WordPress REST API (`/wp-json/wp/v2/`). It may not work with WordPress.com sites that use a different API structure.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.0.51 | 2026-04-28 | [77478](https://github.com/airbytehq/airbyte/pull/77478) | Update dependencies |
| 0.0.49 | 2026-04-09 | [76063](https://github.com/airbytehq/airbyte/pull/76063) | Add configurable lookback window to incremental streams to prevent data loss; fix tab character in pages stream request parameter |
| Version | Date       | Pull Request | Subject                                                                               |
| ------- | ---------- | ------------ | ------------------------------------------------------------------------------------- |
| 0.0.50 | 2026-04-21 | [76792](https://github.com/airbytehq/airbyte/pull/76792) | Update dependencies |
| 0.0.49 | 2026-04-03 | [76063](https://github.com/airbytehq/airbyte/pull/76063) | Add 1-hour lookback window to incremental streams to prevent data loss during DST transitions; fix tab character in pages stream request parameter |
| 0.0.48 | 2026-03-31 | [75861](https://github.com/airbytehq/airbyte/pull/75861) | Update dependencies |
| 0.0.47 | 2026-03-24 | [74691](https://github.com/airbytehq/airbyte/pull/74691) | Update dependencies |
| 0.0.46 | 2026-03-03 | [74149](https://github.com/airbytehq/airbyte/pull/74149) | Update dependencies |
| 0.0.45 | 2026-02-17 | [73511](https://github.com/airbytehq/airbyte/pull/73511) | Update dependencies |
| 0.0.44 | 2026-01-27 | [72050](https://github.com/airbytehq/airbyte/pull/72050) | Update dependencies |
| 0.0.43 | 2026-01-14 | [71483](https://github.com/airbytehq/airbyte/pull/71483) | Update dependencies |
| 0.0.42 | 2025-12-18 | [70682](https://github.com/airbytehq/airbyte/pull/70682) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70195](https://github.com/airbytehq/airbyte/pull/70195) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69649](https://github.com/airbytehq/airbyte/pull/69649) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68929](https://github.com/airbytehq/airbyte/pull/68929) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68373](https://github.com/airbytehq/airbyte/pull/68373) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67932](https://github.com/airbytehq/airbyte/pull/67932) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67324](https://github.com/airbytehq/airbyte/pull/67324) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66457](https://github.com/airbytehq/airbyte/pull/66457) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65666](https://github.com/airbytehq/airbyte/pull/65666) | Update dependencies |
| 0.0.33 | 2025-08-24 | [65432](https://github.com/airbytehq/airbyte/pull/65432) | Update dependencies |
| 0.0.32 | 2025-08-10 | [64860](https://github.com/airbytehq/airbyte/pull/64860) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64324](https://github.com/airbytehq/airbyte/pull/64324) | Update dependencies |
| 0.0.30 | 2025-07-27 | [64091](https://github.com/airbytehq/airbyte/pull/64091) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63637](https://github.com/airbytehq/airbyte/pull/63637) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63192](https://github.com/airbytehq/airbyte/pull/63192) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62750](https://github.com/airbytehq/airbyte/pull/62750) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62239](https://github.com/airbytehq/airbyte/pull/62239) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61780](https://github.com/airbytehq/airbyte/pull/61780) | Update dependencies |
| 0.0.24 | 2025-06-15 | [61196](https://github.com/airbytehq/airbyte/pull/61196) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60745](https://github.com/airbytehq/airbyte/pull/60745) | Update dependencies |
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
| 0.0.1 | 2024-10-21 | 46378 | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>

</HideInUI>
