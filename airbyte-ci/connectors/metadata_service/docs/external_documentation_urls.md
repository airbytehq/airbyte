# External Documentation URLs Guide

## Overview

This guide explains how to identify, scrape, and maintain `externalDocumentationUrls` in connector `metadata.yaml` files. These URLs point to official vendor documentation that helps users understand API changes, authentication requirements, rate limits, and other critical information.

### Purpose

External documentation URLs serve several key purposes:
- Surface vendor changelogs and release notes for tracking breaking changes
- Provide quick access to authentication and permissions documentation
- Link to rate limits and quota information
- Direct users to official API references and data model documentation
- Connect users with vendor status pages and developer communities

### Schema Location

The schema is defined in `airbyte-ci/connectors/metadata_service/lib/metadata_service/models/src/ConnectorMetadataDefinitionV0.yaml`.

The `externalDocumentationUrls` field is an optional array where each entry contains:
- `title` (required): Display title for the documentation link
- `url` (required): URL to the external documentation
- `type` (optional): Category of documentation (see taxonomy below)
- `requiresLogin` (optional, default: false): Whether the URL requires authentication to access

## Documentation Type Taxonomy

### api_release_history
**Description:** Changelogs, release notes, API version history, and out-of-cycle changes.

**Typical URL patterns:**
- `*/changelog*`
- `*/release-notes*`
- `*/api/versions*`
- `*/whats-new*`

**Examples:**
- Airtable: `https://airtable.com/developers/web/api/changelog`
- Google Ads: `https://developers.google.com/google-ads/api/docs/release-notes`
- Salesforce: `https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm`
- Facebook Marketing: `https://developers.facebook.com/docs/marketing-api/marketing-api-changelog`

### api_reference
**Description:** API documentation, versioning docs, technical references, and API specifications.

**Typical URL patterns:**
- `*/api/reference*`
- `*/api/docs*`
- `*/developers/api*`
- `*/api-reference*`

**Examples:**
- GitLab: `https://docs.gitlab.com/ee/api/rest/`
- Chargebee: `https://apidocs.chargebee.com/docs/api/versioning`
- Azure Blob Storage: `https://learn.microsoft.com/en-us/rest/api/storageservices/`
- Pinecone: `https://docs.pinecone.io/reference/api/introduction`

### api_deprecations
**Description:** Deprecation notices, future breaking changes, and migration timelines.

**Typical URL patterns:**
- `*/deprecations*`
- `*/breaking-changes*`
- `*/sunset*`
- `*/migration*`

**Examples:**
- GitLab: `https://docs.gitlab.com/ee/api/rest/deprecations.html`
- Facebook Marketing: `https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/`
- Stripe: `https://stripe.com/docs/upgrades#api-versions`

### authentication_guide
**Description:** Official OAuth/API key setup, consent flows, and authentication methods.

**Typical URL patterns:**
- `*/oauth*`
- `*/authentication*`
- `*/auth*`
- `*/api-keys*`
- `*/credentials*`

**Examples:**
- Airtable: `https://airtable.com/developers/web/api/oauth-reference`
- Google Cloud: `https://cloud.google.com/iam/docs/service-accounts`
- Salesforce: `https://help.salesforce.com/s/articleView?id=sf.connected_app_create.htm`
- Snowflake: `https://docs.snowflake.com/en/user-guide/key-pair-auth`

### permissions_scopes
**Description:** Required roles, permissions, OAuth scopes, or database GRANTs.

**Typical URL patterns:**
- `*/permissions*`
- `*/scopes*`
- `*/roles*`
- `*/access-control*`
- `*/grants*`

**Examples:**
- BigQuery: `https://cloud.google.com/bigquery/docs/access-control`
- Salesforce: `https://help.salesforce.com/s/articleView?id=sf.connected_app_create_api_integration.htm`
- Google Ads: `https://developers.google.com/google-ads/api/docs/oauth/overview`
- Postgres: `https://www.postgresql.org/docs/current/sql-grant.html`

### rate_limits
**Description:** Rate limits, quotas, throttling behavior, and concurrency limits.

**Typical URL patterns:**
- `*/rate-limits*`
- `*/quotas*`
- `*/limits*`
- `*/throttling*`

**Examples:**
- BigQuery: `https://cloud.google.com/bigquery/quotas`
- GitHub: `https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting`
- Salesforce: `https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/`
- Stripe: `https://stripe.com/docs/rate-limits`

### status_page
**Description:** Vendor status/uptime pages for incident tracking.

**Typical URL patterns:**
- `status.*`
- `*/status*`
- `*/system-status*`

**Examples:**
- Snowflake: `https://status.snowflake.com/`
- Google Cloud: `https://status.cloud.google.com/`
- Salesforce: `https://status.salesforce.com/`
- GitHub: `https://www.githubstatus.com/`

### data_model_reference
**Description:** Object/field/endpoint reference for SaaS APIs (what tables/fields exist).

**Typical URL patterns:**
- `*/object-reference*`
- `*/data-model*`
- `*/schema*`
- `*/objects*`

**Examples:**
- Salesforce: `https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/`
- HubSpot: `https://developers.hubspot.com/docs/api/crm/understanding-the-crm`
- GitHub: `https://docs.github.com/en/rest/overview/resources-in-the-rest-api`

### sql_reference
**Description:** SQL dialect/reference docs for databases and warehouses.

**Typical URL patterns:**
- `*/sql-reference*`
- `*/sql/reference*`
- `*/language-reference*`

**Examples:**
- BigQuery: `https://cloud.google.com/bigquery/docs/reference/standard-sql`
- Snowflake: `https://docs.snowflake.com/en/sql-reference`
- Postgres: `https://www.postgresql.org/docs/current/sql.html`
- Redshift: `https://docs.aws.amazon.com/redshift/latest/dg/c_SQL_reference.html`

### migration_guide
**Description:** Vendor migration/breaking-change guides between versions.

**Typical URL patterns:**
- `*/migration*`
- `*/upgrade*`
- `*/version-migration*`

**Examples:**
- Stripe: `https://stripe.com/docs/upgrades`
- Elasticsearch: `https://www.elastic.co/guide/en/elasticsearch/reference/current/breaking-changes.html`

### developer_community
**Description:** Official forums/communities for vendor Q&A and technical discussions.

**Typical URL patterns:**
- `community.*`
- `*/community*`
- `*/forum*`
- `*/discussions*`

**Examples:**
- Airtable: `https://community.airtable.com/development-apis-11`
- Salesforce: `https://developer.salesforce.com/forums`
- Snowflake: `https://community.snowflake.com/`

### other
**Description:** Catch-all for documentation that doesn't fit other categories. Use sparingly.

**Note:** Since `type` is optional, prefer omitting the type field rather than using "other" when a link doesn't fit neatly into a category.

## How to Find Documentation URLs

### Preferred Sources (in order of priority)
1. **Official vendor documentation** (e.g., `docs.vendor.com`, `developers.vendor.com`)
2. **Official vendor blogs** (e.g., `blog.vendor.com`, `developers.vendor.com/blog`)
3. **Official community forums** (e.g., `community.vendor.com`)

### Search Query Templates

Use these search patterns to find appropriate documentation:

```
# Release notes / changelogs
site:<vendor-domain> "release notes"
site:<vendor-domain> "changelog"
site:<vendor-domain> "API changelog"

# API reference
site:<vendor-domain> "API reference"
site:<vendor-domain> "API documentation"

# Authentication
site:<vendor-domain> "OAuth"
site:<vendor-domain> "authentication"
site:<vendor-domain> "API key"

# Permissions
site:<vendor-domain> "permissions"
site:<vendor-domain> "scopes"
site:<vendor-domain> "access control"

# Rate limits
site:<vendor-domain> "rate limits"
site:<vendor-domain> "quotas"
site:<vendor-domain> "API limits"

# Status page
site:status.<vendor-domain>
"<vendor>" status page

# SQL reference (for databases/warehouses)
site:<vendor-domain> "SQL reference"
site:<vendor-domain> "language reference"
```

### URL Selection Heuristics

1. **Prefer canonical, version-agnostic URLs** that are updated over time rather than version-specific pages
   - ✅ Good: `https://docs.vendor.com/api/changelog`
   - ❌ Avoid: `https://docs.vendor.com/v2.3/api/changelog`

2. **Avoid locale-specific paths** when generic URLs exist
   - ✅ Good: `https://docs.vendor.com/api/reference`
   - ❌ Avoid: `https://docs.vendor.com/en-us/api/reference`

3. **Prefer stable root pages** over deep-linked anchors that may change
   - ✅ Good: `https://docs.vendor.com/rate-limits`
   - ⚠️ Use with caution: `https://docs.vendor.com/api#rate-limits-section`

4. **Always use official vendor domains** - never third-party mirrors or documentation aggregators

5. **Set `requiresLogin: true`** when the URL requires authentication to access

## Connector Family-Specific Guidance

### Data Warehouses (BigQuery, Snowflake, Redshift, Databricks)

**Priority types to include:**
- `sql_reference` (required) - SQL dialect documentation
- `authentication_guide` - Service account, key pair, or IAM auth
- `permissions_scopes` - Required roles and grants
- `api_release_history` - Release notes for API/driver changes
- `status_page` - Service status monitoring
- `rate_limits` - Query limits, concurrency limits (if applicable)

**Example (BigQuery):**
```yaml
externalDocumentationUrls:
  - title: Release notes
    url: https://cloud.google.com/bigquery/docs/release-notes
    type: api_release_history
  - title: Standard SQL reference
    url: https://cloud.google.com/bigquery/docs/reference/standard-sql
    type: sql_reference
  - title: Service account authentication
    url: https://cloud.google.com/iam/docs/service-accounts
    type: authentication_guide
  - title: Access control and permissions
    url: https://cloud.google.com/bigquery/docs/access-control
    type: permissions_scopes
  - title: Quotas and limits
    url: https://cloud.google.com/bigquery/quotas
    type: rate_limits
  - title: Google Cloud Status
    url: https://status.cloud.google.com/
    type: status_page
```

### Databases (Postgres, MySQL, MSSQL, MongoDB)

**Priority types to include:**
- `sql_reference` (for SQL databases) - SQL dialect documentation
- `authentication_guide` - Connection and authentication methods
- `permissions_scopes` - User permissions and grants
- `api_release_history` - Version release notes (if applicable)

**Example (Postgres):**
```yaml
externalDocumentationUrls:
  - title: PostgreSQL documentation
    url: https://www.postgresql.org/docs/current/
    type: api_reference
  - title: SQL reference
    url: https://www.postgresql.org/docs/current/sql.html
    type: sql_reference
  - title: Authentication methods
    url: https://www.postgresql.org/docs/current/auth-methods.html
    type: authentication_guide
  - title: GRANT permissions
    url: https://www.postgresql.org/docs/current/sql-grant.html
    type: permissions_scopes
```

### SaaS APIs (Salesforce, HubSpot, GitHub, Stripe)

**Priority types to include:**
- `api_release_history` (required) - Changelogs and release notes
- `api_reference` - API documentation
- `api_deprecations` - Deprecation schedules (if available)
- `authentication_guide` - OAuth or API key setup
- `permissions_scopes` - Required scopes or permissions
- `rate_limits` - API rate limits
- `data_model_reference` - Object/field reference
- `developer_community` - Developer forums
- `status_page` - Service status

**Example (Salesforce):**
```yaml
externalDocumentationUrls:
  - title: API release notes
    url: https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm
    type: api_release_history
  - title: REST API reference
    url: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/
    type: api_reference
  - title: Connected app OAuth
    url: https://help.salesforce.com/s/articleView?id=sf.connected_app_create.htm
    type: authentication_guide
  - title: OAuth scopes
    url: https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_tokens_scopes.htm
    type: permissions_scopes
  - title: API rate limits
    url: https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/
    type: rate_limits
  - title: Object reference
    url: https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/
    type: data_model_reference
  - title: Salesforce Status
    url: https://status.salesforce.com/
    type: status_page
```

### Vector Stores (Pinecone, Weaviate, Qdrant, Chroma)

**Priority types to include:**
- `api_reference` (required) - API documentation
- `rate_limits` - Request limits and quotas
- `authentication_guide` - API key or authentication setup
- `api_release_history` - Release notes (if available)
- `status_page` - Service status (if available)
- `migration_guide` - Version migration guides (if versions differ significantly)

**Example (Pinecone):**
```yaml
externalDocumentationUrls:
  - title: API reference
    url: https://docs.pinecone.io/reference/api/introduction
    type: api_reference
  - title: Authentication
    url: https://docs.pinecone.io/guides/get-started/authentication
    type: authentication_guide
  - title: Rate limits
    url: https://docs.pinecone.io/troubleshooting/rate-limits
    type: rate_limits
  - title: Release notes
    url: https://docs.pinecone.io/release-notes
    type: api_release_history
```

## Maintenance Guidelines

### Link Stability Checks

Periodically validate that external documentation URLs are still accessible:

1. **HTTP status validation** - Check that URLs return 200 or 3xx status codes
2. **Flag 4xx/5xx errors** - Document broken links for replacement
3. **Set `requiresLogin: true`** when appropriate to avoid false positives

**Simple validation script:**
```bash
# Check a single URL
curl -I -L -s -o /dev/null -w "%{http_code}" "https://docs.vendor.com/api/changelog"

# Expected: 200, 301, 302
# Action needed: 404, 403, 500
```

### Update Cadence

- **Quarterly sweep** - Review all external documentation URLs for broken links
- **On vendor announcements** - Update when vendors announce major documentation restructuring
- **On deprecation notices** - Add `api_deprecations` links when vendors announce breaking changes

### Replacement Rules

When updating broken or outdated links:

1. **Prefer same domain** - Look for the new location on the same vendor domain
2. **Check vendor consolidation** - Vendors may consolidate multiple doc sites into one
3. **Update to canonical** - If vendor provides a redirect, update to the final destination
4. **Document in PR** - Note why the link was changed in the PR description

### PR Review Practices

When reviewing PRs that add or modify external documentation URLs:

1. **Spot-check 2-3 links** per connector to verify they're accessible and relevant
2. **Verify type categorization** - Ensure the `type` field matches the content
3. **Check for duplicates** - Avoid adding the same URL twice with different titles
4. **Validate requiresLogin** - Confirm whether authentication is actually required

## YAML Template

Here's a canonical example showing multiple types:

```yaml
externalDocumentationUrls:
  - title: Release notes
    url: https://cloud.google.com/bigquery/docs/release-notes
    type: api_release_history
  - title: Standard SQL reference
    url: https://cloud.google.com/bigquery/docs/reference/standard-sql
    type: sql_reference
  - title: Service account authentication
    url: https://cloud.google.com/iam/docs/service-accounts
    type: authentication_guide
  - title: Access control and permissions
    url: https://cloud.google.com/bigquery/docs/access-control
    type: permissions_scopes
  - title: Quotas and limits
    url: https://cloud.google.com/bigquery/quotas
    type: rate_limits
  - title: Google Cloud Status
    url: https://status.cloud.google.com/
    type: status_page
    requiresLogin: false
```

## Validation Checklist

Before submitting a PR with external documentation URLs:

- [ ] Schema validation passes (run `poetry run metadata_service validate <metadata.yaml> <doc.md>`)
- [ ] All URLs return HTTP 200 or 3xx status codes
- [ ] No paywalls or login requirements (unless `requiresLogin: true` is set)
- [ ] URLs are canonical and version-agnostic when possible
- [ ] Type categorization is accurate
- [ ] No duplicate URLs with different titles
- [ ] Official vendor domains only (no third-party mirrors)
- [ ] Titles are descriptive and consistent with vendor terminology

## Common Pitfalls to Avoid

1. **Don't over-categorize** - If a link doesn't fit neatly, omit the `type` field rather than forcing it
2. **Avoid version-specific URLs** - Prefer evergreen URLs that are updated over time
3. **Don't link to third-party docs** - Always use official vendor documentation
4. **Watch for locale redirects** - Some URLs may redirect based on browser locale
5. **Don't assume status pages exist** - Not all vendors have public status pages
6. **Avoid deep anchors** - Deep-linked sections may change; prefer stable root pages
7. **Don't duplicate content** - If a single page covers multiple topics, link it once with the most specific type

## Examples by Connector Type

### Example: Snowflake (Data Warehouse)
```yaml
externalDocumentationUrls:
  - title: Release notes
    url: https://docs.snowflake.com/en/release-notes
    type: api_release_history
  - title: SQL reference
    url: https://docs.snowflake.com/en/sql-reference
    type: sql_reference
  - title: Key pair authentication
    url: https://docs.snowflake.com/en/user-guide/key-pair-auth
    type: authentication_guide
  - title: Access control
    url: https://docs.snowflake.com/en/user-guide/security-access-control
    type: permissions_scopes
  - title: Snowflake Status
    url: https://status.snowflake.com/
    type: status_page
```

### Example: Stripe (SaaS API)
```yaml
externalDocumentationUrls:
  - title: API changelog
    url: https://stripe.com/docs/upgrades#api-changelog
    type: api_release_history
  - title: API reference
    url: https://stripe.com/docs/api
    type: api_reference
  - title: API versioning and upgrades
    url: https://stripe.com/docs/upgrades
    type: migration_guide
  - title: Authentication
    url: https://stripe.com/docs/keys
    type: authentication_guide
  - title: Rate limits
    url: https://stripe.com/docs/rate-limits
    type: rate_limits
  - title: Stripe Status
    url: https://status.stripe.com/
    type: status_page
```

### Example: Postgres (Database)
```yaml
externalDocumentationUrls:
  - title: PostgreSQL documentation
    url: https://www.postgresql.org/docs/current/
    type: api_reference
  - title: SQL commands
    url: https://www.postgresql.org/docs/current/sql-commands.html
    type: sql_reference
  - title: Client authentication
    url: https://www.postgresql.org/docs/current/client-authentication.html
    type: authentication_guide
  - title: Database roles and privileges
    url: https://www.postgresql.org/docs/current/user-manag.html
    type: permissions_scopes
```

## Regenerating Schema After Changes

If you modify the schema enum in `ConnectorMetadataDefinitionV0.yaml`, regenerate the generated models:

```bash
cd airbyte-ci/connectors/metadata_service/lib
poetry install
poetry run poe generate-models
```

This will update:
- `metadata_service/models/generated/ConnectorMetadataDefinitionV0.json`
- `metadata_service/models/generated/ConnectorMetadataDefinitionV0.py`

## Bulk Update Best Practices

When adding external documentation URLs to multiple connectors at scale (e.g., 50+ connectors), follow these practices to maintain clean diffs and efficient review cycles:

### Surgical Text Insertion Approach

**Problem:** Using YAML parsing libraries (PyYAML, ruamel.yaml) to modify metadata.yaml files can cause massive diff noise by reformatting the entire file, converting inline arrays to block style, and triggering format-fix bots.

**Solution:** Use surgical text insertion to add only the `externalDocumentationUrls` section without re-parsing the entire file.

**Implementation:**
```python
def add_external_docs_surgical(metadata_path: Path, docs_urls: list[dict]) -> bool:
    """
    Add externalDocumentationUrls using surgical text insertion.
    Inserts the new section at the end of the data block.
    
    Returns True if the file was modified, False if it already had externalDocumentationUrls.
    """
    content = metadata_path.read_text()
    
    # Check if externalDocumentationUrls already exists
    if 'externalDocumentationUrls:' in content:
        return False
    
    # Format the new YAML section manually
    new_section = format_external_docs_yaml(docs_urls)
    
    lines = content.split('\n')
    
    # Find the last line that belongs to the data block
    last_data_line_idx = -1
    in_data_block = False
    
    for i, line in enumerate(lines):
        if line.startswith('data:'):
            in_data_block = True
            continue
        
        if in_data_block:
            # Check if this line is part of the data block (starts with 2+ spaces)
            if line and not line.startswith(' '):
                # We've exited the data block
                break
            elif line.strip():  # Non-empty line in data block
                last_data_line_idx = i
    
    if last_data_line_idx == -1:
        return False
    
    # Insert the new section after the last data line
    lines.insert(last_data_line_idx + 1, new_section)
    
    # Write back
    new_content = '\n'.join(lines)
    metadata_path.write_text(new_content)
    
    return True
```

### Batching Strategy

**Recommended batch size:** 50 connectors per PR
- Small enough for efficient review (5-10 minutes per PR)
- Large enough to make systematic progress
- Allows for quick iteration if issues are found

**Grouping approach:**
- Group A: All destination connectors (86 total)
- Groups B-M: Source connectors in alphabetical order (50 per group)

### Commit Message Format

Use `[skip ci]` flag to bypass CI checks for metadata-only changes:
```bash
git commit -m "feat: Add external documentation URLs to Group X connectors [skip ci]"
```

**Rationale:** Metadata-only changes don't require version bumps or connector releases. CI failures for "Connector Version Increment Check" are expected and can be ignored.

### PR Review Efficiency

**Results from 13-group rollout (673 connectors):**
- Clean diffs: Only insertions, no deletions or formatting changes
- Fast reviews: ~5 minutes per PR with surgical text insertion
- High success rate: 658/673 connectors updated (97.8%)
- Average: 2.2 documentation URLs per connector

**Key metrics:**
- Total documentation URLs collected: 1,459
- Coverage: 99.9% of connectors (670/671)
- Most common types: api_reference (95.7%), authentication_guide (54.3%), rate_limits (26.6%)

### File Structure Handling

Some metadata.yaml files have `metadataSpecVersion` at the top, others at the bottom. The surgical insertion script must:
1. Find the last line of the data block
2. Insert the new section after it
3. Preserve all existing formatting

### Verification Steps

Before pushing changes:
1. Verify surgical text insertion produces only insertions (no deletions)
2. Review git diff to ensure only externalDocumentationUrls sections changed
3. Run pre-commit hooks locally to catch issues before pushing
4. Spot-check 2-3 connectors to verify URLs are accessible

## Additional Resources

- [Connector Metadata Schema](../lib/metadata_service/models/src/ConnectorMetadataDefinitionV0.yaml)
- [Metadata Service README](../lib/README.md)
- [Connector Development Guide](https://docs.airbyte.com/connector-development/)
