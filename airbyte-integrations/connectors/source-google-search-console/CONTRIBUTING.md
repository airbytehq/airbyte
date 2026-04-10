# source-google-search-console: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-google-search-console` that deviate
from standard declarative connector patterns. Read this before making changes to the connector.

---

## 1. POST-Based Search Analytics with Keys Array Response Format

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

## 2. Configurable Rate Limits with Low Default Quotas

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

## 3. AggregationType Override for Compatibility

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
