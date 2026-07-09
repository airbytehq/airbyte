# Confluence migration guide

## Upgrading to 1.0.0

Version `1.0.0` migrated the `blog_posts`, `pages`, and `space` streams from the
Confluence REST API v1 to the Confluence REST API v2. This change updates endpoint
paths and stream schemas. To ensure a seamless transition, follow the migration
steps outlined below.

### Key changes

- **Blog Posts**
  - **Endpoint change:** `GET /wiki/rest/api/content?type=blogpost` to `GET /wiki/api/v2/blogposts`
  - **Breaking change:** Schema changes require updating existing integrations.

- **Pages**
  - **Endpoint change:** `GET /wiki/rest/api/content?type=page` to `GET /wiki/api/v2/pages`
  - **Breaking change:** Schema changes require adjustments.

- **Spaces**
  - **Endpoint change:** `GET /wiki/rest/api/space` to `GET /wiki/api/v2/spaces`
  - **Breaking change:** Schema changes require migration.

### Migration steps

1. Upgrade to version `1.0.0` or later.
2. Reset and synchronize the `blog_posts`, `pages`, and `space` streams so Airbyte
   discovers the new schemas and refreshes existing records.

For more details, see the [Confluence REST API v2 documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/).
