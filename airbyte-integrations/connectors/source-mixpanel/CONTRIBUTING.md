# source-mixpanel: Unique Behaviors

This document describes the biggest non-obvious gotchas in `source-mixpanel` that deviate from
standard declarative connector patterns. Read this before making changes to the connector.

The connector is declarative (low-code) with custom Python components in
`source_mixpanel/components.py`.

---

## 1. Query API Rate Limit: 60 Queries per Hour

Mixpanel's Query API allows a maximum of **60 queries per hour and 5 concurrent queries**
([Mixpanel rate limits](https://developer.mixpanel.com/reference/rate-limits)). The connector enforces
this with an API budget (`MovingWindowCallRatePolicy` with `limit: 1` per `PT60S`), configured both in
`manifest.yaml` (`api_budget`) and as the module-level `DEFAULT_API_BUDGET` in
`source_mixpanel/backoff_strategy.py`, which `MixpanelHttpRequester` assigns to `self.api_budget`.

**Why this matters:** Every stream shares this single low budget, so syncs are throttled to roughly one
request per minute regardless of how many streams run. When adding a new stream or requester, keep it on
the shared budget — issuing requests outside the budget risks tripping Mixpanel's per-hour limit and
getting the project rate-limited.

---

## 2. Export Stream Returns JSONL That Can Split a Record Across Lines

The `export` stream reads from Mixpanel's Raw Event Export API, which streams **JSON Lines**, not a
single JSON document. Occasionally a single record is split across multiple lines in the response. The
custom `iter_dicts` helper (used by `ExportDpathExtractor`) reassembles these: it parses each line as
JSON and, when a line fails to parse, buffers it and retries joining adjacent parts. It also short-circuits
when Mixpanel emits the literal line `terminated early`, logging a warning instead of raising.

The extractor deliberately consumes `response.iter_lines(decode_unicode=True)` rather than
`response.text.splitlines()`, because splitting on text mis-parses records whose property values contain
embedded line breaks.

**Why this matters:** The export response cannot be parsed as ordinary JSON. Any change to export
extraction must preserve the line-reassembly logic, or records with embedded newlines (or records split
mid-stream) will be silently dropped — this is the class of "missing records / stuck read" issue the
export stream has historically hit.

---

## 3. Export Error Handler: Retry on ConnectionResetError and Timezone Mismatch

`ExportErrorHandler` (a `DefaultErrorHandler` subclass) adds two export-specific cases:

- It pre-parses the streamed response with `iter_dicts` so that a `ConnectionResetError` raised mid-parse
  is caught and turned into a transient-error **retry** instead of a hard failure.
- It handles the `400` response with message `to_date cannot be later than today`, which indicates a
  project-timezone mismatch. `ExportHttpRequester` defaults the project timezone to `US/Pacific`
  (`default_project_timezone`) and derives `end_date` from `pendulum.today(tz=project_timezone)` minus a
  one-day lookback, so a wrong `project_timezone` config can push `to_date` past Mixpanel's "today".

**Why this matters:** Export failures are frequently environmental (dropped connection) or
config-driven (timezone), not connector bugs. Removing this handler would surface those as fatal errors.

---

## 4. Export Lookback Windows and the `where` Time Filter

`ExportHttpRequester.get_request_params` combines several config values to bound each export slice:

- `from_date` is the slice `start_time` shifted back by `from_date_lookback_window`, which is the larger
  of `export_lookback_window` and `attribution_window * 24 * 60 * 60`.
- `to_date` is the connector's computed `end_date`.
- A `where` filter (`properties["$time"]>=datetime(<epoch>)`) is added using `start_time` shifted back by
  `export_lookback_window`, so re-requested windows are re-filtered on the event `$time` property.

**Why this matters:** `from_date`/`to_date` are coarse day-level bounds, while the `where` clause applies
the finer second-level cursor. Changing one without the other will either miss late-arriving events
(attribution window) or re-emit already-synced records.

---

## 5. Engage Properties Are Returned Keyed by Field Name, Not as a List

The engage/engage-properties endpoints return properties as a dict keyed by field name rather than as an
array. `EngagePropertiesDpathExtractor` flattens this by injecting each key back into its value object as
`name` and yielding the resulting list. `EngagePaginationStrategy` paginates engage using both a
`session_id` (returned on the first page) and an incrementing `page`, tracking `total` from the first page
to decide when to stop, and resets that `total` on `reset()`.

**Why this matters:** Engage pagination is stateful across pages (`session_id` + running `total`), which
is unlike simple page/offset pagination. Any refactor must preserve the first-page `total` capture and the
`reset()` behavior, or pagination will terminate early or loop.

## Incremental Stream Considerations

Mixpanel streams are defined declaratively in `manifest.yaml` with custom Python components. The
high-volume `export` stream is incremental via a `time`/`$time` cursor with the lookback and `where`
handling described above; several lower-volume streams (e.g. `annotations`, `cohorts`, `funnels`) are
config-style or parent lookups.

**Connector type:** Declarative manifest with Python custom components.

**Analysis status:** A full stream-by-stream incremental analysis table (per the standard
CONTRIBUTING.md schema) should be added by a future agent after reviewing the manifest stream
definitions, their cursor fields, and the corresponding Mixpanel API endpoints.
