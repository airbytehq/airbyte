# source-hubspot: Unique Connector Behaviors

## Overview

HubSpot CRM source connector using the declarative (low-code) framework with extensive custom Python
components in `components.py`. The connector syncs data from HubSpot's CRM, marketing, and engagement
APIs.


## Key Files

- `manifest.yaml` -- Declarative stream definitions, authentication, pagination, error handling, and
  schemas (~7600 lines).
- `components.py` -- Custom Python components for behaviors that cannot be expressed in YAML alone.
- `CONTRIBUTING.md` -- **Read this first.** Documents all non-obvious connector-specific behaviors
  including hidden API calls during extraction, dual-endpoint selection, pagination workarounds, and
  property chunking. Understanding these behaviors is critical before making changes.


## Important Patterns

- CRM search streams make additional association API calls inside the record extractor. See
  `CONTRIBUTING.md` section 1.
- The engagements stream dynamically selects between two different API endpoints. See `CONTRIBUTING.md`
  section 2.
- Pagination resets at 10,000 results for search endpoints. See `CONTRIBUTING.md` section 3.
- Custom objects use `StateDelegatingStream` with two different sub-stream implementations. See
  `CONTRIBUTING.md` section 4.
- Many streams use character-based property chunking (15,000 char limit). See `CONTRIBUTING.md` section 5.
- Authentication retries on 401 to handle mid-sync token expiration. See `CONTRIBUTING.md` section 8.


This document describes the biggest non-obvious gotchas in `source-hubspot` that deviate from standard
declarative connector patterns. Read this before making changes to the connector.

---

## 1. HubspotAssociationsExtractor: Hidden API Calls Inside Record Extraction

The CRM search streams (contacts, companies, deals, tickets, leads, engagements_*, deal_splits) use
`HubspotAssociationsExtractor` as their record extractor. This extractor does **not** simply parse the
HTTP response -- it makes **additional batch POST requests** to the HubSpot Associations v4 API
(`/crm/v4/associations/{entity}/{association}/batch/read`) for every page of results.

HubSpot's CRM v3 Search API does not return association data inline with object records. To get
associations (e.g., which contacts are linked to a deal), you must make separate calls to the
Associations v4 batch read endpoint, passing in the record IDs from the primary response. This is a
fundamental limitation of HubSpot's API design -- there is no way to include association data in a
single search request.

**Why this matters:** Each page of CRM search results silently triggers N additional API calls -- one per association type configured on that stream. For example, the `deals` stream fetches associations for companies, contacts, and line items, so every single page of deals costs 4 HTTP requests total (1 search + 3 association batches). Adding a new association to a stream's config quietly increases API usage across every page of every sync.

---

## 2. EngagementsHttpRequester: Dual-Endpoint Selection at Runtime

The `engagements` stream dynamically chooses between two completely different HubSpot API endpoints at
runtime:

- **Recent Engagements API** (`/engagements/v1/engagements/recent/modified`): Used when the start
  date/state is within the last 29 days **AND** the total record count is <= 10,000.
- **All Engagements API** (`/engagements/v1/engagements/paged`): Used in all other cases.

Both are HubSpot legacy v1 endpoints. The Recent API is optimized for low-volume recent changes but
has a hard cap of 10,000 records and only covers the last 30 days. The All API has no such limits but
returns every engagement ever created, requiring client-side filtering. HubSpot does not offer a single
v1 endpoint that efficiently handles both cases, which is why the connector implements this switching
logic.

**Why this matters:** The connector makes a hidden probe request at the start of every sync to decide which endpoint to use, and that decision is locked in for the entire sync. The two endpoints have different page size limits (100 vs 250) and different data coverage (30-day window vs all-time). **Do not add `step` to the incremental sync config** -- the dual-endpoint logic requires a single slice from start_date to now.

---

## 3. HubspotCRMSearchPaginationStrategy: 10,000-Result Limit Workaround

HubSpot's CRM Search API (`POST /crm/v3/objects/{entity}/search`) enforces a hard limit of 10,000
total results per query. This is documented in
[HubSpot's API reference](https://developers.hubspot.com/docs/api/crm/search): attempting to page
beyond offset 10,000 returns a 400 error. The limit applies per-query, not per-account -- you can
issue multiple queries with different filters to access more data.

The custom pagination strategy works around this by:

1. Tracking the current offset (`after`) and detecting when it approaches 10,000.
2. When the limit is reached, resetting `after` to 0 and adding an `id` filter using the last
   record's `hs_object_id + 1` to effectively start a new query window.
3. The CRM search request body includes a `sorts` clause ordering by `hs_object_id ASCENDING` and a
   filter `hs_object_id >= {id}` to ensure deterministic ordering and seamless continuation.

This is necessary because HubSpot's search endpoint was designed for filtered discovery, not bulk
export. The 10,000 limit is intentional on HubSpot's side and cannot be increased.

**Why this matters:** Without this workaround, any CRM object type with more than 10,000 modified records since the last sync would silently stop paginating and miss data. The pagination token is a dict with two possible shapes (`{"after": N}` or `{"after": N, "id": M}`), not a simple cursor string, so any code touching page tokens must handle both. This affects all CRM search streams: contacts, companies, deals, tickets, leads, all engagement subtypes, deal_splits, and custom objects.

---

## 4. StateDelegatingStream for Custom Objects

Custom HubSpot objects use `DynamicDeclarativeStream` with `StateDelegatingStream` to select between
two completely different stream implementations based on whether incoming stream state exists:

- **No state (full refresh):** Uses `GET /crm/v3/objects/{entity}` with property chunking and
  `GroupByKeyMergeStrategy` to merge chunked responses by `id`.
- **Has state (incremental):** Uses `POST /crm/v3/objects/{entity}/search` with the CRM search
  pagination strategy and date range filters.

This split exists because HubSpot's CRM Search API requires filter parameters that depend on knowing a
cursor position (i.e., state). On first sync with no state, it is more reliable to use the simpler
list endpoint which returns all objects without needing filter constraints. The search endpoint is more
efficient for incremental syncs because it supports `lastmodifieddate` filters, avoiding full scans.

**Why this matters:** These are two completely independent stream implementations that happen to share a name. They have different requesters, paginators, and record selectors, so a fix applied to one sub-stream will not carry over to the other. If you change how custom objects sync, you need to verify both the full-refresh and incremental paths separately.

---

## 5. Property Chunking with Character-Based Limits

Many streams use `PropertyChunking` to split property requests into chunks with a **15,000 character
limit** (not a count limit). This affects property history streams (companies, contacts, deals),
archived streams, forms, custom objects, and base CRM object streams (goals, products, line_items).

HubSpot's CRM v3 list endpoints accept property names as query parameters (e.g.,
`?properties=name,email,phone,...`). Because HubSpot accounts can have hundreds of custom properties
with long names, the resulting URL can exceed HTTP URL length limits imposed by HubSpot's
infrastructure and intermediary proxies. HubSpot does not document a specific URL length limit, but
the connector uses a 15,000 character threshold as a conservative safe maximum based on observed
failures. Properties are fetched dynamically from `/properties/v2/{entity}/properties` and then split
into character-bounded chunks.

**Why this matters:** This means what looks like a single page of 100 records may actually require N parallel HTTP requests behind the scenes (one per property chunk), all stitched together before being emitted. If a user adds many custom properties to their HubSpot objects, the number of HTTP calls per page silently multiplies. CRM search streams (POST) send properties in the request body and don't need chunking -- only GET-based list endpoints are affected.

---

## 6. Per-Record API Enrichment (Campaigns and Marketing Emails)

Two streams make **additional API calls during record transformation** to enrich each record:

- **Campaigns:** HubSpot's campaign list endpoint (`/email/public/v1/campaigns`) only returns a
  summary with `id`, `appId`, `appName`, and `lastUpdatedTime`. To get full campaign details
  (subject, counters, etc.), the connector makes a separate GET request to
  `/email/public/v1/campaigns/{id}` for each record. This is a limitation of HubSpot's email campaign
  API which has no "list with full details" endpoint.
- **Marketing Emails:** HubSpot's v3 email API separates content data and performance statistics into
  different endpoints. For every email record, the connector makes a GET request to
  `/marketing/v3/emails/{emailId}/statistics` to fetch performance metrics.

**Why this matters:** Unlike the association extractor (which batches per page), these enrichments make one extra HTTP call per individual record. A sync of 50,000 campaigns means 50,000 additional API calls on top of the pagination calls. This is the most API-intensive pattern in the connector and the most likely to hit rate limits on large accounts.

---

## 7. Mixed Datetime Formats Across Streams

HubSpot's API uses inconsistent datetime formats across different endpoint versions:

- **Legacy v1 endpoints** (engagements, campaigns, deal_pipelines, workflows, email_events,
  subscription_changes, form_submissions) return **millisecond Unix timestamps** (e.g.,
  `1672531200000`). The connector uses the `%ms` format string for these.
- **CRM v3 endpoints** (contacts, companies, deals, tickets, etc.) return **ISO 8601 strings** with
  varying precision:
  - `%Y-%m-%dT%H:%M:%S.%fZ` (with milliseconds, e.g., `2023-01-01T00:00:00.000Z`)
  - `%Y-%m-%dT%H:%M:%SZ` (without fractional seconds)
  - `%Y-%m-%dT%H:%M:%S%z` (with timezone offset)

This inconsistency stems from HubSpot's gradual API evolution -- v1 endpoints were designed around
Unix timestamps, while v3 adopted ISO 8601. HubSpot has not standardized across versions and the v1
endpoints are still actively used for resources not yet available in v3.

Additionally, previous versions of the connector stored state values as millisecond strings even for
streams that now use ISO 8601. Most streams list multiple `cursor_datetime_formats` to handle both
current API responses and legacy state values. The `MigrateEmptyStringState` migration (used by nearly
every incremental stream) also handles a legacy bug where previous connector versions stored empty
strings as cursor values.

**Why this matters:** If you add a new stream and configure the wrong datetime format, cursor comparisons will silently break -- either skipping records or re-syncing everything on every run. Most streams list multiple `cursor_datetime_formats` to handle both current API responses and legacy state values from older connector versions.

---

## 8. Authentication: 401 Retry

The error handler retries on HTTP 401 (authentication expired). This is unusual -- most connectors
fail immediately on 401. HubSpot OAuth access tokens have a 30-minute lifetime, and for long-running
syncs the token can expire mid-sync. The `OAuthAuthenticator` transparently refreshes the token on
retry, making this seamless. Without this retry, any sync lasting longer than 30 minutes would fail
partway through.

The connector also handles HTTP 530 (Cloudflare Origin DNS Error) as a credentials failure. HubSpot
returns this non-standard status code when the API token format is incorrect, rather than a standard
401 or 403.

HubSpot uses standard OAuth 2.0 with long-lived refresh tokens via `/oauth/v1/token`. Unlike
source-airtable (short-lived refresh tokens) or source-gong (requires config update after token
exchange), HubSpot's refresh tokens do not expire and do not require special handling.

---

## 9. API Rate Budget: Differentiated Rate Limits

HubSpot enforces different rate limits depending on the API category. The connector models this with
two separate rate limit policies:

- **CRM Search endpoints** (`POST /crm/v3/objects/*/search`): 5 requests/second, 300 requests/minute.
  [HubSpot documents this](https://developers.hubspot.com/docs/api/crm/search) as a stricter limit
  specifically for search operations.
- **All other endpoints:** 10 requests/second, 100 requests per 10 seconds. HubSpot's general limit
  for OAuth apps is 110 requests per 10 seconds.

The error handler uses dual backoff on 429 responses: first the `Retry-After` header, then exponential
backoff as fallback. This dual approach is necessary because HubSpot does not always include the
`Retry-After` header on 429 responses.
