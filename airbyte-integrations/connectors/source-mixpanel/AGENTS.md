> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-mixpanel: Unique Behaviors

This document describes the biggest non-obvious gotchas in `source-mixpanel` that deviate from
standard connector patterns. Read this before making changes to the connector.

---

## 1. Hybrid Connector: Declarative Streams Plus a Python `Export` Stream

`source-mixpanel` is a `YamlDeclarativeSource`, but it is **not** fully declarative. `SourceMixpanel.streams()`
takes the declarative streams from `manifest.yaml` and then appends a Python `Export` stream from
`source_mixpanel/streams.py`:

- Declarative streams (registered in `manifest.yaml` `streams:`): `cohorts`, `engage`, `annotations`,
  `cohort_members`, `funnels` (with `funnel_ids` as a parent).
- Python stream (appended in `source.py`): `export` (`streams.py` `Export`), which also uses the internal
  Python `ExportSchema` stream to build its dynamic schema.

**Why this matters:** The `export` stream is implemented in `streams.py`, not in the manifest. Changes to
export behavior belong in `streams.py`; the other five streams are defined declaratively in `manifest.yaml`
with Python custom components in `components.py`.

---

## 2. Two Different Rate-Limit Enforcement Mechanisms (60 Queries/Hour)

Mixpanel's Query API allows a maximum of **60 queries per hour and 5 concurrent queries**
([Mixpanel rate limits](https://developer.mixpanel.com/reference/rate-limits)). Because of the hybrid
design above, the two stream families enforce this differently:

- **Declarative streams** use a CDK API budget: `MovingWindowCallRatePolicy` with `limit: 1` per `PT60S`,
  configured in `manifest.yaml` (`api_budget`) and mirrored as `DEFAULT_API_BUDGET` in
  `backoff_strategy.py`, which `MixpanelHttpRequester` assigns to `self.api_budget`.
- **The Python `Export`/`ExportSchema` streams** (base class `MixpanelStream`) instead **sleep** after each
  request: `parse_response` calls `time.sleep(3600 / reqs_per_hour_limit)` (default `reqs_per_hour_limit=60`
  → a 60-second sleep per request). `ExportSchema` sets `reqs_per_hour_limit=0` to skip the sleep while
  generating the dynamic schema.

**Why this matters:** There is no single place that governs throttling. A change to the manifest
`api_budget` does not affect the Python export stream, and vice versa.

---

## 3. `export` Stream Returns JSONL That Can Split a Record Across Lines

The `export` stream reads Mixpanel's Raw Event Export API, which streams **JSON Lines**, not a single JSON
document (`Export.request_kwargs` sets `stream=True`). Occasionally a single record is split across
multiple lines. `Export.iter_dicts` (`streams.py`) reassembles these: it parses each line as JSON and,
when a line fails to parse, buffers it and retries joining adjacent parts. It short-circuits when Mixpanel
emits the literal line `terminated early`, logging a warning instead of raising. `Export.process_response`
consumes `response.iter_lines(decode_unicode=True)` (not `response.text.splitlines()`, which mis-parses
records whose property values contain embedded line breaks), then flattens/renames properties.

**Why this matters:** The export response cannot be parsed as ordinary JSON. Any change to export
extraction must preserve the line-reassembly logic, or records with embedded newlines (or records split
mid-stream) will be silently dropped — this is the class of "missing records / stuck read" issue the
export stream has historically hit.

---

## 4. `export` Timezone Mismatch Stops the Stream

The export error handling lives in `streams.py` `ExportErrorHandler` (an `HttpStatusErrorHandler` subclass
returned by `Export.get_error_handler`). A `400` whose body contains `to_date cannot be later than today`
sets the stream's `_timezone_mismatch = True` and returns `ResponseAction.IGNORE` with a `config_error`
("Your project timezone must be misconfigured…"). `DateSlicesMixin` then short-circuits `parse_response`
and `stream_slices`, so the stream **stops** rather than failing hard. This happens because the project
timezone (default `US/Pacific`) is used to compute `end_date` (`today - 1 day`); a wrong `project_timezone`
pushes `to_date` past Mixpanel's "today". The handler also maps `Unable to authenticate request` and `402`
to `FAIL`.

**Why this matters:** A timezone misconfiguration surfaces as a silently stopped export rather than a hard
failure, so check the project timezone if the `export` stream returns no data.

---

## 5. `export` Lookback Windows and the `where` Time Filter

The Python `Export` stream bounds each slice using several config values:

- `DateSlicesMixin.stream_slices` shifts `start_date` back by
  `final_lookback_window = max(export_lookback_window, attribution_window * 24 * 60 * 60)` and clamps
  `end_date` to `min(end_date, today(project_timezone))`. `from_date`/`to_date` request params are the
  resulting day-level slice bounds.
- `Export.request_params` additionally injects a finer filter
  `where = properties["$time"]>=datetime(<epoch>)` from the cursor value, because `from_date`/`to_date` only
  filter by date.

**Why this matters:** `from_date`/`to_date` are coarse day-level bounds while the `where` clause applies the
finer second-level cursor. Changing one without the other will either miss late-arriving events (attribution
window) or re-emit already-synced records.

---

## 6. Engage Properties Are Returned Keyed by Field Name, Not as a List

The declarative `engage` stream uses Python custom components. The engage/engage-properties endpoints return
properties as a dict keyed by field name rather than as an array; `EngagePropertiesDpathExtractor`
(`components.py`) flattens this by injecting each key back into its value object as `name` and yielding the
resulting list. `EngagePaginationStrategy` paginates engage using both a `session_id` (returned on the first
page) and an incrementing `page`, tracking `total` from the first page to decide when to stop, and resets
that `total` on `reset()`.

**Why this matters:** Engage pagination is stateful across pages (`session_id` + running `total`), unlike
simple page/offset pagination. Any refactor must preserve the first-page `total` capture and the `reset()`
behavior, or pagination will terminate early or loop.

## Incremental Stream Considerations

The connector mixes declarative and Python streams (see §1). The high-volume `export` stream is a Python
incremental stream keyed on `time`/`$time` with the lookback and `where` handling in §5; the declarative
streams (`cohorts`, `engage`, `annotations`, `cohort_members`, `funnels`) are defined in `manifest.yaml`.

**Connector type:** Hybrid — declarative manifest (with Python custom components) plus a legacy Python
`Export` stream.

**Analysis status:** A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md
schema) should be added by a future agent after reviewing both the manifest stream definitions and the
Python `Export`/`ExportSchema` streams in `streams.py`.
