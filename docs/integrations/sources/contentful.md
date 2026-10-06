# Contentful
Contentful is a headless content management system (CMS) that stores structured content and delivers it through APIs. This connector reads published content from one Contentful space and environment using the read-only Content Delivery API: the content model (content types), entries, assets, locales, and tags. Entries for every content type are synced into a single entries stream; join entries.content_type_id to content_types.id to split them by type. Draft (unpublished) content and deletions are not captured.

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
| content_types | id | DefaultPaginator | ✅ |  ✅  |
| entries | id | DefaultPaginator | ✅ |  ✅  |
| assets | id | DefaultPaginator | ✅ |  ✅  |
| locales | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-06 | | Initial release by [@paulb17](https://github.com/paulb17) via Connector Builder |

</details>
