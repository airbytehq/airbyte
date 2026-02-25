# source-hubspot: Unique Connector Behaviors

This document describes non-obvious, connector-specific behaviors in `source-hubspot` that deviate from
standard declarative connector patterns. Read this before making changes to the connector.

---

## 1. HubspotAssociationsExtractor: Hidden API Calls Inside Record Extraction

**Files:** `components.py` (`HubspotAssociationsExtractor`, `build_associations_retriever`), `manifest.yaml` (`base_crm_search_incremental_stream`)

The CRM search streams (contacts, companies, deals, tickets, leads, engagements_*, deal_splits) use
`HubspotAssociationsExtractor` as their record extractor. This extractor does **not** simply parse the
HTTP response -- it makes **additional batch POST requests** to the HubSpot Associations v4 API
(`/crm/v4/associations/{entity}/{association}/batch/read`) for every page of results.

**Why this matters:**
- Each page of CRM search results triggers N additional API calls (one per association type per batch).
  For example, the `deals` stream fetches associations for `companies`, `contacts`, and `line_items`,
  so every page of deal results triggers 3 additional API calls.
- The `build_associations_retriever()` function in `components.py` manually constructs a full
  `SimpleRetriever` with its own `SelectiveAuthenticator`, `HttpRequester`, error handler, and
  `ListPartitionRouter` -- all in Python code rather than YAML. This is because the low-code framework
  does not support instantiating a `SimpleRetriever` outside of a `DeclarativeStream` context.
- If you add a new association to a stream's `associations` list, you are adding an extra API call per
  page of results. Consider rate limit impact.
- The associations retriever sends record IDs in the POST body via `extra_fields` on the `StreamSlice`,
  which is an unusual data-passing pattern.

---

## 2. EngagementsHttpRequester: Dual-Endpoint Selection at Runtime

**Files:** `components.py` (`EngagementsHttpRequester`), `manifest.yaml` (`engagements_stream`)

The `engagements` stream dynamically chooses between two completely different API endpoints at runtime:

- **Recent Engagements API** (`/engagements/v1/engagements/recent/modified`): Used when the start
  date/state is within the last 29 days **AND** the total record count is <= 10,000.
- **All Engagements API** (`/engagements/v1/engagements/paged`): Used in all other cases.

**Why this matters:**
- On the first request, `should_use_recent_api()` makes a **probe request** to the Recent API to check
  the `total` field in the response. This is an extra API call that happens before any data is fetched.
- The Recent API has a hard cap of 10,000 most recently updated records. If exceeded, the connector
  silently falls back to the All API, which returns everything but requires client-side incremental
  filtering (`is_client_side_incremental: true`).
- The page size is set to 250 (All API max), but if the Recent API is selected, HubSpot silently
  clamps it to 100.
- The decision is cached for the entire sync via `_use_recent_api`, so it cannot switch mid-sync.
- The stream uses a single slice from start_date to now (no step/windowing), which is required for the
  dual-endpoint logic to work. Do not add `step` to the incremental sync config.

---

## 3. HubspotCRMSearchPaginationStrategy: 10,000-Result Limit Workaround

**Files:** `components.py` (`HubspotCRMSearchPaginationStrategy`), `manifest.yaml` (`base_crm_search_incremental_stream`)

HubSpot's `/search` API has a hard limit of 10,000 total results per query. Attempting to paginate
beyond 10,000 returns a 400 error. This custom pagination strategy works around the limit by:

1. Tracking the current offset (`after`) and detecting when it approaches 10,000.
2. When the limit is reached, resetting `after` to 0 and adding an `id` filter using the last
   record's `hs_object_id + 1` to start a new query window.
3. The CRM search request body includes a `sorts` clause ordering by `hs_object_id ASCENDING` and a
   filter `hs_object_id >= {id}` to support this reset mechanism.

**Why this matters:**
- The pagination token is a dict (`{"after": N}` or `{"after": N, "id": M}`), not a simple cursor
  string. Code that inspects or manipulates page tokens must handle both shapes.
- The search request body in the manifest references `next_page_token['next_page_token'].get('id', 0)`
  and `next_page_token['next_page_token']['after']`, which is tightly coupled to this strategy.
- This applies to all streams inheriting from `base_crm_search_incremental_stream`.

---

## 4. StateDelegatingStream for Custom Objects

**Files:** `manifest.yaml` (`dynamic_streams` section)

Custom HubSpot objects use `DynamicDeclarativeStream` with `StateDelegatingStream` to select between
two completely different stream implementations based on whether incoming stream state exists:

- **No state (full refresh):** Uses `GET /crm/v3/objects/{entity}` with property chunking and
  `GroupByKeyMergeStrategy` to merge chunked responses by `id`.
- **Has state (incremental):** Uses `POST /crm/v3/objects/{entity}/search` with the CRM search
  pagination strategy and date range filters.

**Why this matters:**
- The two sub-streams have different requesters, paginators, and record selectors. Changes to one do
  not automatically apply to the other.
- The `HttpComponentsResolver` fetches custom object schemas from `/crm/v3/schemas` and dynamically
  injects the object name, entity identifier, and property list into both sub-stream templates via
  `components_mapping`.
- The `fullyQualifiedName` is used as the entity path parameter (e.g., `p_{name}` if
  `fullyQualifiedName` is not available), which differs from standard CRM objects.
- Custom objects use `HubspotCustomObjectsSchemaLoader` to generate schemas from the properties
  returned by the components resolver, rather than the `DynamicSchemaLoader` used by standard streams.

---

## 5. Property Chunking with Character-Based Limits

**Files:** `manifest.yaml` (multiple streams)

Many streams use `PropertyChunking` to split property requests into chunks with a **15,000 character
limit** (not a count limit). This is used in:

- Property history streams (companies, contacts, deals) -- properties sent as URL query parameters via
  `QueryProperties` + `propertiesWithHistory`
- Archived streams (deals_archived) -- properties sent as URL query parameters with
  `GroupByKeyMergeStrategy` to merge chunked responses by `id`
- Forms stream -- same pattern as archived streams
- Custom objects (full refresh sub-stream) -- same pattern as archived streams
- Base CRM object streams (goals, products, line_items) -- properties sent as URL query parameters

**Why this matters:**
- The 15,000 character limit exists because HubSpot's API (and intermediary proxies) have URL length
  restrictions. Properties are fetched dynamically from `/properties/v2/{entity}/properties`.
- Streams that use chunking with `record_merge_strategy: GroupByKeyMergeStrategy` make multiple API
  requests per page and merge results client-side. This multiplies API call volume proportionally to
  the number of property chunks.
- The CRM search streams (`base_crm_search_incremental_stream`) handle properties differently: they
  use `fetch_properties_from_endpoint` on the requester, which sends all properties in the POST body
  rather than URL params, avoiding the URL length issue.

---

## 6. NewtoLegacyFieldTransformation: Dynamic V2-to-Legacy Field Mapping

**Files:** `components.py` (`NewtoLegacyFieldTransformation`), `manifest.yaml` (contacts, deals, deals_archived streams)

HubSpot renamed fields between API versions (v1 -> v2). This transformation dynamically maps new field
names back to their legacy equivalents to prevent breaking existing syncs. The mapping is prefix-based
and applies to dynamically-named fields:

- `hs_v2_date_entered_{stage_id}` -> `hs_date_entered_{stage_id}`
- `hs_v2_date_exited_{stage_id}` -> `hs_date_exited_{stage_id}`
- `hs_v2_latest_time_in_{stage_id}` -> `hs_time_in_{stage_id}`
- For contacts: `hs_v2_date_entered_{stage_id}` -> `hs_lifecyclestage_{stage_id}_date`

**Why this matters:**
- The `{stage_id}` portion is user-generated (deal pipeline stages, lifecycle stages), so the
  transformation cannot use static field lists -- it must pattern-match at runtime.
- The contacts stream has a special case: `hs_lifecyclestage_` mappings append `_date` to the
  transformed field name if not already present.
- This transformation applies to both records and schemas (via `deals_archived_schema_loader` and
  dynamic schema loaders for contacts/deals).

---

## 7. AddFieldsFromEndpointTransformation: Per-Record API Enrichment

**Files:** `components.py` (`AddFieldsFromEndpointTransformation`, `MarketingEmailStatisticsTransformation`), `manifest.yaml` (campaigns, marketing_emails streams)

Two streams make **additional API calls during record transformation** to enrich each record:

- **Campaigns:** For every campaign record, makes a GET request to
  `/email/public/v1/campaigns/{id}` to fetch full campaign details and merges them into the record.
- **Marketing Emails:** For every email record, makes a GET request to
  `/marketing/v3/emails/{emailId}/statistics` to fetch email statistics and merges them into the
  record.

**Why this matters:**
- This means these streams make 1 additional API call per record (not per page). For large datasets,
  this can result in thousands of extra API calls.
- The `MarketingEmailStatisticsTransformation` has error handling that logs warnings but doesn't fail
  the sync if statistics are unavailable for individual emails. The campaigns transformation does not
  have this safety net.

---

## 8. HubspotPropertyHistoryExtractor: Flattening Versioned Properties into Records

**Files:** `components.py` (`HubspotPropertyHistoryExtractor`), `manifest.yaml` (companies/contacts/deals property history streams)

Property history streams yield **one record per property version change**, not one record per entity.
The extractor iterates over `propertiesWithHistory` in each API response entity and yields individual
records for each historical version of each property.

**Why this matters:**
- A single API entity (e.g., one contact) can produce dozens or hundreds of records if it has many
  property changes over time.
- The extractor explicitly skips `hs_lastmodifieddate` history to avoid redundant records (every
  property change also updates `lastmodifieddate`, which would double the output).
- Primary keys are composite: `(entity_id, property_name, timestamp)`.
- The contacts property history stream applies field renaming transformations to convert v3 camelCase
  fields back to v1 kebab-case (e.g., `sourceId` -> `source-id`) for backwards compatibility.
- These streams use `is_client_side_incremental: true` with a cursor on `timestamp`, and support a
  legacy `%ms` (millisecond string) state format via `MigrateEmptyStringState`.

---

## 9. EntitySchemaNormalization: HubSpot-Specific Type Coercion

**Files:** `components.py` (`EntitySchemaNormalization`)

Custom schema normalization handles several HubSpot API quirks:

- **Empty strings:** Converted to `None` for non-string field types (HubSpot returns `""` instead of
  `null` for empty fields).
- **Numeric strings:** Cast to `int` if the string is purely numeric, otherwise `float`. This prevents
  numeric IDs from being cast to floats. Handles non-castable values gracefully (e.g.,
  `"3092727991;3881228353"` for a field typed as `number`) by logging and returning the original.
- **Boolean strings:** `"true"`/`"false"` converted to actual booleans.
- **Datetime parsing:** Attempts seconds-precision parsing first, then milliseconds. Handles float
  timestamp strings by truncating the decimal before parsing. Returns original value on parse failure
  rather than raising an error.

---

## 10. Authentication: 401 Retry and Dual Auth Support

**Files:** `manifest.yaml` (error handlers, authenticator definitions)

- **401 Retry:** The error handler retries on HTTP 401 (authentication expired). This is unusual --
  most connectors fail on 401. This exists because HubSpot OAuth access tokens can expire mid-sync,
  and the `OAuthAuthenticator` will transparently refresh the token on retry.
- **530 Cloudflare Error:** The connector handles HTTP 530 (Cloudflare Origin DNS Error) as a FAIL
  with a credentials-related message, because HubSpot returns this status when the API token format
  is incorrect.
- **SelectiveAuthenticator:** Supports two auth methods selected by `credentials.credentials_title`:
  `"OAuth Credentials"` (OAuthAuthenticator with client_id/client_secret/refresh_token) and
  `"Private App Credentials"` (BearerAuthenticator with a static access token).
- **Standard OAuth behavior:** HubSpot uses a standard OAuth 2.0 flow with long-lived refresh tokens.
  The token refresh endpoint is `/oauth/v1/token`. Unlike connectors such as source-airtable (which
  has short-lived refresh tokens) or source-gong (which requires updating the source config after
  token exchange), HubSpot's refresh tokens do not expire and do not require special handling.

---

## 11. API Rate Budget: Differentiated Rate Limits

**Files:** `manifest.yaml` (`api_budget` section)

The connector implements two separate rate limit policies:

- **CRM Search endpoints** (`POST /crm/v3/objects/*/search`): 5 requests/second, 300 requests/minute.
- **All other endpoints:** 10 requests/second, 100 requests per 10 seconds.

HubSpot accounts are limited to 110 requests per 10 seconds overall. The error handler uses dual
backoff: first `Retry-After` header, then exponential backoff as fallback (HubSpot does not always
include `Retry-After` on 429 responses).

---

## 12. MigrateEmptyStringState: Legacy State Handling

**Files:** `components.py` (`MigrateEmptyStringState`), `manifest.yaml` (most incremental streams)

Almost every incremental stream uses `MigrateEmptyStringState` to handle a legacy issue where previous
connector versions stored empty strings (`""`) as cursor values in stream state. The migration replaces
empty string state with the configured `start_date` (or the default `2006-06-01T00:00:00.000Z`).

Some streams also specify a `cursor_format` (e.g., `"%ms"`) to convert the start_date into the
appropriate format for that stream's cursor field.

---

## 13. Mixed Datetime Formats Across Streams

The connector handles multiple datetime formats because HubSpot's API is inconsistent across endpoints:

- `%ms` -- Millisecond Unix timestamps (used by legacy v1 endpoints: engagements, campaigns,
  deal_pipelines, workflows, email_events, subscription_changes, form_submissions)
- `%Y-%m-%dT%H:%M:%S.%fZ` -- ISO 8601 with millisecond precision (used by v3 CRM endpoints)
- `%Y-%m-%dT%H:%M:%SZ` -- ISO 8601 without fractional seconds
- `%Y-%m-%dT%H:%M:%S%z` -- ISO 8601 with timezone offset

Most streams list multiple `cursor_datetime_formats` to handle both current API responses and legacy
state values. The contacts property history stream explicitly notes: "Previous version of Hubspot
stored state as a millisecond string for some reason."
