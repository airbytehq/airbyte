# source-hubspot: Unique Connector Behaviors

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

**Why this matters:**
- Each page of CRM search results triggers N additional API calls (one per association type). For
  example, the `deals` stream fetches associations for `companies`, `contacts`, and `line_items`, so
  every page of deal results triggers 3 extra API calls.
- The `build_associations_retriever()` function manually constructs a full `SimpleRetriever` with its
  own `SelectiveAuthenticator`, `HttpRequester`, error handler, and `ListPartitionRouter` entirely in
  Python code. This is because the low-code framework does not support instantiating a
  `SimpleRetriever` outside of a `DeclarativeStream` context.
- Adding a new association to a stream's `associations` list adds an extra API call per page. Consider
  rate limit impact.

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

**Why this matters:**
- On the first request, `should_use_recent_api()` makes a **probe request** to the Recent API to check
  the `total` field in the response. This is an extra API call before any data is fetched.
- The Recent API silently clamps page size to 100 even though the stream requests 250 (the All API
  max).
- The decision is cached for the entire sync, so it cannot switch mid-sync.
- The stream uses a single slice from start_date to now (no step/windowing), which is required for
  the dual-endpoint logic to work. **Do not add `step` to the incremental sync config.**

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

**Why this matters:**
- The pagination token is a dict (`{"after": N}` or `{"after": N, "id": M}`), not a simple cursor
  string. Code that inspects or manipulates page tokens must handle both shapes.
- The search request body in the manifest references `next_page_token['next_page_token'].get('id', 0)`
  and `next_page_token['next_page_token']['after']`, which is tightly coupled to this strategy.
- This applies to all streams inheriting from `base_crm_search_incremental_stream` (contacts,
  companies, deals, tickets, leads, engagements_calls/emails/meetings/notes/tasks, deal_splits) as
  well as the incremental sub-stream for custom objects.

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

**Why this matters:**
- The two sub-streams have different requesters, paginators, and record selectors. Changes to one do
  not automatically apply to the other.
- The `HttpComponentsResolver` fetches custom object schemas from `/crm/v3/schemas` and dynamically
  injects the object name, entity identifier, and property list into both sub-stream templates.

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

**Why this matters:**
- Streams that use chunking with `record_merge_strategy: GroupByKeyMergeStrategy` make **multiple API
  requests per page** and merge results client-side by record `id`. This multiplies API call volume
  proportionally to the number of property chunks. An account with many custom properties will consume
  significantly more API quota.
- The CRM search streams handle properties differently: they send all properties in the POST request
  body rather than URL params, avoiding the URL length issue entirely. This is why search streams do
  not need property chunking.
- If you're adding a stream that uses HubSpot's CRM list endpoints (GET), you likely need property
  chunking. If you're using search endpoints (POST), you don't.

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

**Why this matters:**
- These streams make **1 additional API call per record** (not per page). For large datasets, this
  results in thousands of extra API calls and is the most API-intensive pattern in the connector.
- The marketing emails enrichment has error handling that logs warnings but doesn't fail the sync if
  statistics are unavailable. The campaigns enrichment does not have this safety net.

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

**Why this matters:**
- When adding a new stream, you must check which datetime format the HubSpot endpoint actually returns
  and configure `cursor_datetime_formats` accordingly. Getting this wrong will cause silent data loss
  or sync failures.

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
