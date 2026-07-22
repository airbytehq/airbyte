# source-zoho-crm: Unique Behaviors

## 1. Dynamic Module-Based Stream Generation

This connector generates streams at runtime from Zoho CRM module metadata. The `ZohoStreamFactory.produce()` method in `streams.py`:

1. Fetches all available modules via `/crm/v2/settings/modules`.
2. Filters to API-supported modules (`module.api_supported`).
3. For each module, fetches field metadata via `/crm/v2/settings/fields?module={module_name}` and module-specific settings via `/crm/v2/settings/modules/{module_name}`.
4. Dynamically creates a Python class per module using `type()`, inheriting from `IncrementalZohoCrmStream`.
5. Each stream is named `Incremental{module.api_name}ZohoCRMStream` and reads from `/crm/v2/{module.api_name}`.

## 2. Region-Specific API Endpoints

Zoho CRM supports multiple data center regions (US, AU, EU, IN, CN, JP). The `ZohoAPI` class constructs the correct API base URL based on the user's `dc_region` config, and the environment setting (production, developer, sandbox) determines a URL prefix.

## 3. Concurrency Based on Zoho Edition

The connector adjusts its concurrent request limit based on the user's Zoho CRM edition (Free: 5, Standard: 10, Professional: 15, Enterprise: 20, Ultimate: 25) via `_CONCURRENCY_API_LIMITS` in `api.py`.

## Incremental Stream Considerations

This connector generates streams at runtime from Zoho CRM module metadata via `ZohoStreamFactory`. User inputs that drive stream generation are: the authenticated user's Zoho CRM org, their edition (which determines rate limits), the data center region, and the environment (production/developer/sandbox). The connector's incremental story is **comprehensive by default**: every dynamically generated stream inherits from `IncrementalZohoCrmStream`, which uses `Modified_Time` as its cursor field and the Zoho CRM `If-Modified-Since` HTTP header for server-side filtering. All modules that pass the `api_supported` check are created as incremental streams.

| Stream Type / Pattern | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| `zoho_module` (all user-accessible CRM modules: Leads, Contacts, Accounts, Deals, etc.) | medium–large (varies by module and org size) | top-level dynamic | `Modified_Time` | `modified_since` — Zoho CRM API supports `If-Modified-Since` header which returns HTTP 304 (Not Modified) when no records have changed since the specified timestamp | `incremental` | All dynamically generated streams use `IncrementalZohoCrmStream` (`streams.py:70-105`). The cursor is tracked in stream state and incremented as records are read. The `If-Modified-Since` header is injected via `request_headers()` with a 1-second offset to prevent duplicate reads. The API returns a `204 No Content` or `304 Not Modified` for modules with no changes, handled by `EMPTY_BODY_STATUSES`. |

### Deferred & framework-level work

1. **No gaps identified.** All dynamically generated streams are already incremental with `Modified_Time` cursor and server-side `If-Modified-Since` filtering. This is the ideal state for a dynamic-stream connector.
2. **Potential optimization: pagination + modified-since interaction.** The current implementation sends `If-Modified-Since` as a request header. If a module has millions of records modified since the cursor, all are returned across paginated responses. The Zoho CRM API also supports a `modified_since` query parameter in some contexts. Verify whether combining cursor-based filtering with pagination improves performance for high-volume modules.
3. **Module-specific quirks.** Some Zoho CRM modules return `204 No Content` even on initial requests if the module has no records. The connector handles this via `EMPTY_BODY_STATUSES` in `streams.py:24`, but new modules added by Zoho CRM should be tested for compatibility with the `If-Modified-Since` header behavior.
4. **Missing `start_datetime` validation.** The `IncrementalZohoCrmStream` falls back to `1970-01-01T00:00:00+00:00` when `start_datetime` is not configured. For very old orgs, this could result in a long initial sync. Consider validating or defaulting to a more recent start date.
