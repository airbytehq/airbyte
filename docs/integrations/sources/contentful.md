# Contentful
Contentful is a headless content management system (CMS) that stores structured content and delivers it through APIs. This connector reads published content from one Contentful space and environment using the read-only Content Delivery API: the content model (content types), entries, assets, locales, and tags. Entries for every content type are synced into a single entries stream; join entries.content_type_id to content_types.id to split them by type. Draft (unpublished) content and deletions are not captured.

## Prerequisites

- A Contentful space ID.
- A Content Delivery API (CDA) access token for that space.

## Setup guide

1. In the Contentful web app, open the space and go to **Settings > API keys**.
2. Select an existing API key or click **Add API key**.
3. Copy the **Space ID** and the **Content Delivery API - access token**. The Content Preview API token is not supported: the connector reads from `cdn.contentful.com`, which only accepts CDA tokens.
4. In Airbyte, enter the token and space ID. Optionally set the environment (defaults to `master`), a locale, and a start date.

## Limitations

- Only published content is synced. Drafts, and changes that have not been published, are not returned by the Content Delivery API.
- Deletions are not captured. A deleted or unpublished entry or asset stops appearing in the API, but rows already synced are not removed.
- If `locale` is left blank, entries and assets are returned in the space's default locale only. Set it to a specific locale code (for example, `en-US`) to sync another locale.
- Pagination uses `skip`/`limit` offsets, ordered by `sys.updatedAt`. If entries or assets are published while a long sync is paging, the result set shifts, so a record can be read twice or skipped. Duplicates are harmless with a deduplicated sync mode, because the incremental filter (`sys.updatedAt[gte]`) is inclusive and records share the `id` primary key. A skipped record is synced the next time it is updated, or on a full refresh.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `locale` | `string` | Locale. Locale code to request for entry/asset fields (e.g. en-US). Leave blank to use the space&#39;s default locale. |  |
| `space_id` | `string` | Space ID. Contentful space ID. |  |
| `cda_token` | `string` | Content Delivery API token. Contentful Content Delivery API (read-only) access token. |  |
| `start_date` | `string` | Start Date. Earliest sys.updatedAt to sync on the first incremental run (ISO 8601). | 2015-01-01T00:00:00.000Z |
| `environment` | `string` | Environment. Contentful environment. Defaults to master. | master |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| content_types | id | DefaultPaginator | ✅ |  ❌  |
| entries | id | DefaultPaginator | ✅ |  ✅  |
| assets | id | DefaultPaginator | ✅ |  ✅  |
| locales | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-06 | [88148](https://github.com/airbytehq/airbyte/pull/88148)| Initial release by [@paulb17](https://github.com/paulb17) via Connector Builder |

</details>
