# source-google-search-console: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-google-search-console` that deviate
from standard declarative connector patterns. Read this before making changes to the connector.

---

## 1. Two-Level Nested Substream State Migration

Search Analytics streams are partitioned by two dimensions: `site_url` and `search_type`. The legacy
state format stored cursors in a two-level nested structure
(`{ "https://example.com/": { "web": { "date": "2025-05-25" } } }`), but the current declarative
framework's `LegacyToPerPartitionStateMigration` only handles one level of nesting.

The custom `NestedSubstreamStateMigration` handles this two-level migration by iterating over
site URLs as the outer key and search types as the inner key, converting each combination into a
per-partition state entry.

**Why this matters:** If this migration is removed or broken, any connection that was created before the
migration to the declarative framework will lose its cursor positions and re-sync all historical data
from scratch. The migration also intentionally discards the legacy global cursor value because the
previous Python implementation saved an unreliable "last seen partition" value rather than a true global
maximum.

---

## 2. POST-Based Search Analytics with Keys Array Response Format

All Search Analytics streams use POST requests to `/searchAnalytics/query` rather than GET requests.
Google's Search Console API returns dimension values as a positional `keys` array in each row (e.g.,
`{"keys": ["2025-01-01", "US", "DESKTOP"], "clicks": 42}`) rather than as named fields. The connector
must map each position in the `keys` array back to its corresponding dimension name using
`AddFields` transformations.

For built-in streams, this mapping is hardcoded (e.g., `record['keys'][0]` -> `date`,
`record['keys'][1]` -> `country`). For custom report streams, the
`CustomReportExtractDimensionsFromKeys` component handles this dynamically based on the dimensions
configured in the user's custom report.

**Why this matters:** The order of dimensions in the API request body determines the order of values in
the `keys` array response. If you reorder the `dimensions` list in a stream's request body without
updating the corresponding `AddFields` transformations, fields will be silently swapped (e.g., country
values will appear in the device field and vice versa).

---

## 3. Custom Reports with Dynamic Schema Generation

Users can define custom search analytics reports in their config under `custom_reports_array`, selecting
any combination of dimensions (country, date, device, page, query). These are rendered as
`DynamicDeclarativeStream` instances. The `CustomReportSchemaLoader` generates a JSON schema at runtime
based on which dimensions the user selected, mapping each dimension to its schema type using a static
`DIMENSION_TO_PROPERTY_SCHEMA_MAP`.

The `date` dimension is always force-included (even if not specified by the user) because it serves as
the incremental sync cursor field.

**Why this matters:** The schema for custom report streams is not static -- it is computed at runtime
from the user's config. If you add a new possible dimension to the Search Console connector, you must
also add its schema mapping to `DIMENSION_TO_PROPERTY_SCHEMA_MAP` in `CustomReportSchemaLoader`, or
custom reports using that dimension will produce records with untyped fields.

---

## 4. Dual Authentication: OAuth vs Service Account (JWT)

The connector supports two completely different authentication flows via `SelectiveAuthenticator`:
- **OAuth (`Client`):** Standard Google OAuth 2.0 with refresh tokens
- **Service Account (`Service`):** JWT-based authentication using
  `JwtProfileAssertionOAuthAuthenticator` with RS256 signing, a 3600-second token duration, and the
  `webmasters.readonly` scope

The service account flow parses the `service_account_info` JSON string from the config to extract the
private key, client email, and token URI at runtime.

**Why this matters:** These are two fundamentally different auth mechanisms that share nothing beyond the
`SelectiveAuthenticator` switch. The Service Account path involves JWT construction, RS256 signing, and
profile assertion -- if you modify the OAuth flow, the Service Account flow is unaffected and vice
versa. Testing one auth type does not validate the other.

---

## 5. Configurable Rate Limits with Low Default Quotas

Google Search Console has three layers of rate limits: per-site (1,200 req/min max), per-user
(1,200 req/min max), and per-project (40,000 req/min max). However, most new or unbilled Google Cloud
projects start with a quota of only 60 requests per minute, far below the documented maximum.

The connector exposes a `requests_per_minute` config option (default: 1200) and injects it into the
`api_budget` policy. The error handler specifically matches the string `"Search Analytics QPS quota
exceeded"` to classify rate limit errors, using a 60-second constant backoff.

**Why this matters:** The default rate limit of 1200 RPM will immediately cause rate limiting for most
new Google Cloud projects. If customers report 429 errors, the first thing to check is their actual
Google Cloud Console quota and adjust `requests_per_minute` accordingly. The connector also has a
`num_workers` config (default: 3, max: 50) that controls concurrency.

---

## 6. AggregationType Override for Compatibility

Some Google Search Console implementations return a 400 error for certain `aggregationType` values
(`byPage`, `byProperty`). This is customer-specific and depends on how their Search Console property is
configured. The connector provides an `always_use_aggregation_type_auto` boolean config that, when
enabled, overrides all stream-specific `aggregationType` values to `auto`.

The error handler explicitly matches HTTP 400 responses and surfaces a message telling the user to
enable this setting.

**Why this matters:** Without this override, certain streams (like `search_analytics_page_report` which
uses `byPage` or `search_analytics_site_report_by_site` which uses `byProperty`) will fail with a 400
error for some customers. The error looks like a connector bug but is actually a Google API limitation
based on the customer's property type. This config option is the escape hatch.

---

## 7. Config Migration from String to Array Format

The connector migrates the legacy `custom_reports` config (a JSON string) to the current
`custom_reports_array` format (a native array) via `ConfigNormalizationRules`. The migration uses Jinja
interpolation which automatically infers the datatype, so no explicit JSON parsing is needed.

After migration, the config is validated against a schema that enforces required fields (`name`,
`dimensions`) and valid dimension enum values (`country`, `date`, `device`, `page`, `query`).

**Why this matters:** If you modify the custom reports config structure, you must ensure the migration
still works for connections created with the old string-based format. The validation runs after
migration, so invalid legacy configs will surface validation errors rather than silently producing
broken streams.

---

## 8. Search Appearance Keyword Streams as Substreams

The `search_analytics_keyword_*` streams are substreams of a parent `search_appearances` stream. The
parent stream fetches the list of search appearances (rich result types like AMP, FAQ, etc.) for each
site URL and search type combination. Each keyword stream then makes filtered API calls using
`dimensionFilterGroups` to get analytics data for each specific search appearance type.

**Why this matters:** The keyword streams generate one API call per search appearance type per site URL
per search type per date slice. If a site has many search appearance types, the number of API calls
multiplies rapidly. These streams also do not use `NestedSubstreamStateMigration` because they were
added after the migration to the declarative framework.
