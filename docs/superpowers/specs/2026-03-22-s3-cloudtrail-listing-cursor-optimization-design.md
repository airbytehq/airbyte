# S3 CloudTrail Listing & Cursor Optimization

**Date:** 2026-03-22
**Status:** Draft

## Problem

The Airbyte source-s3 connector lists **all files** in the CloudTrail S3 prefix on every sync, regardless of how many have already been synced. For Forter's bucket:

- **35M+ files** spanning 3 years (2023-02 to present)
- **~32k new files/day** across 17 AWS regions (us-east-1 alone: ~24k/day)
- **Listing takes 1.5-3 hours** — every sync, before a single record is processed
- `start_date` only filters client-side; the S3 LIST API still enumerates everything

The cursor compounds the problem:

- Stores `{filename: last_modified}` dict, capped at **10,000 entries**
- Forter generates 24k files/day — overflows the cap immediately
- When full, the CDK falls back to a time-window heuristic that can cause re-syncs or missed files

Meanwhile, CloudTrail's folder structure encodes the date directly: `CloudTrail/{region}/YYYY/MM/DD/filename.json.gz`. We can use this to list only the files we need.

### Benchmarks (real Forter data)

**S3 listing (us-east-1, March 2026 — 800k files):**

| Approach | Time | Files |
|----------|------|-------|
| Single broad prefix (current) | 282s | 800k |
| Parallel per-day prefixes (10 threads) | 93s | 800k |

The current connector uses the broad prefix for the **entire bucket history** (~35M files), not just one month.

**Per-file CPU cost (2,350-record CloudTrail file):**

| Step | Time |
|------|------|
| `orjson.loads` (full file) | 12.7ms |
| Flatten + wrap `{"data": r}` | 0.2ms |
| AirbyteMessage + serialize | 6.6ms |

Parsing is fast. The bottleneck is listing.

## CloudTrail Folder Structure

```
s3://bucket/AWSLogs/{account_id}/CloudTrail/{region}/YYYY/MM/DD/{account}_{CloudTrail}_{region}_{timestamp}_{random}.json.gz
```

- Date is encoded in the path — no need to list files to determine their date
- Files are immutable once written
- File names contain timestamps + random suffix, guaranteed unique
- AWS delivers files within ~15 minutes of the event window

## Design

### 1. Date-Aware Prefix Listing

Override `get_matching_files()` in `SourceS3StreamReader`. When `flatten_records_key` is set (CloudTrail mode):

1. **Determine start date** — from `self._cloudtrail_cursor_date` (set by the cursor, see "Bridging cursor state to the reader" below) or from `start_date` config as fallback
2. **Extract the CloudTrail base prefix** — parse from the configured glob/prefix pattern. The account ID (or org ID for organization trails) is part of the existing prefix config, e.g., `AWSLogs/174522763890/CloudTrail/`. No new config field needed.
3. **Discover regions** — single `list_objects_v2(Prefix='{base_prefix}', Delimiter='/')` call. Returns region "folders" in one fast API call.
4. **Generate day-level prefixes** — `{base_prefix}{region}/YYYY/MM/DD/` for each day from `start_date - 1 day` (overlap buffer) to today (UTC), for each region
5. **List in parallel** — `ThreadPoolExecutor(max_workers=10)` listing day-prefixes concurrently. I/O-bound, GIL-released. 10 threads is the sweet spot from benchmarks (3x speedup, more threads don't help due to S3 rate limits from a single IP).
6. **Yield `RemoteFile` objects** — same interface as before, CDK pipeline downstream is unchanged

**Bridging cursor state to the reader:** The `SourceS3StreamReader` has no direct access to cursor state. The bridge is:
- Add a `_cloudtrail_cursor_date: Optional[datetime]` attribute on `SourceS3StreamReader` (default `None`)
- In `SourceS3._make_default_stream()`, after the cursor's initial state is set, call `self.stream_reader.set_cloudtrail_cursor_date(cursor.cloudtrail_cursor)` to pass the timestamp to the reader
- `get_matching_files()` reads `self._cloudtrail_cursor_date` to determine the start date
- If `_cloudtrail_cursor_date` is None (first sync or no state), falls back to `start_date` from config

**Example:** Cursor says last sync was 2026-03-20, today (UTC) is 2026-03-22:
- Generates: 17 regions × 4 days (19-22, including overlap) = 68 prefixes
- Each completes in <1s
- Total: ~2-3 seconds (vs 1.5 hours currently)

When `flatten_records_key` is NOT set: falls back to existing behavior unchanged.

**First sync with no state and no `start_date`:** If `flatten_records_key` is set but no cursor and no `start_date` exist, fall back to existing broad-prefix listing. The optimization requires a starting date to work.

**Optional config: `cloudtrail_regions`** — list of regions to sync. If not set, auto-discovered. Allows filtering to specific regions.

**Error handling for parallel listing:** If a thread fails (S3 throttle, transient error), retry up to 3 times with exponential backoff. If still failing, raise the error to fail the sync (fail-fast is safer than silently skipping a prefix).

### 2. Date-Based Cursor

Replace the filename-history cursor with a high-water timestamp for CloudTrail connections.

**State format:**

```json
{
  "history": {},
  "_ab_source_file_last_modified": "2026-03-22T15:30:00.000000Z",
  "cloudtrail_cursor": "2026-03-22T15:30:00.000000Z"
}
```

**Behavior:**
- `cloudtrail_cursor` stores the `last_modified` of the most recently synced file
- On sync: listing generates prefixes from `cloudtrail_cursor - 1 day` to today (UTC)
- `_should_sync_file`: returns `True` if `file.last_modified > cloudtrail_cursor`. **Does NOT delegate to `super()`** — the CloudTrail path completely replaces the CDK's history-based logic.
- `add_file`: updates `cloudtrail_cursor` if `file.last_modified > cloudtrail_cursor`. **Does NOT call `super().add_file()`** — skips history population entirely to avoid the 10k cap.
- `_get_cursor`: overridden to return the `cloudtrail_cursor` value (formatted as the CDK expects) so the Airbyte UI shows progress correctly. Without this override, `_get_cursor()` returns `None` for empty history.
- `history` dict stays empty — kept for CDK compatibility, never populated

**Why this works:**
- CloudTrail files are immutable (never modified after creation)
- `LastModified` from S3 is when AWS delivered the file — monotonically increasing
- No need to track filenames — just the high-water mark
- The 1-day overlap buffer handles late-arriving files

**State migration (supports v3 → v4 → v5 path):**
- If `cloudtrail_cursor` is present in state: use new logic (v5)
- If absent but `history` has entries (v4 state): extract `max(history.values())` as the initial `cloudtrail_cursor`. Clear history.
- If v3 legacy state: existing v3→v4 conversion runs first, then v4→v5 migration applies
- If no state at all (fresh connection): use `start_date` from config
- From that point forward, use the new v5 format

### 3. Files Changed

| File | Action |
|------|--------|
| `source_s3/v4/stream_reader.py` | **Modify** — add `set_cloudtrail_cursor_date()`, `_discover_regions()`, `_generate_day_prefixes()`, override `get_matching_files()` for CloudTrail mode |
| `source_s3/v4/cursor.py` | **Modify** — add `cloudtrail_cursor` field, override `_should_sync_file` (no super), `add_file` (no super), `_get_cursor`, `get_state`, `set_initial_state` with v4→v5 migration |
| `source_s3/v4/source.py` | **Modify** — in `_make_default_stream()`, bridge cursor state to stream reader via `set_cloudtrail_cursor_date()` |
| `source_s3/v4/config.py` | **Modify** — add optional `cloudtrail_regions` config field |
| `unit_tests/v4/test_cloudtrail_listing.py` | **Create** — tests for date-aware listing |
| `unit_tests/v4/test_cloudtrail_cursor.py` | **Create** — tests for date-based cursor + migration |

### 4. Edge Cases

- **Late-arriving files:** 1-day overlap buffer re-lists the cursor day. Files already synced are filtered by the cursor comparison. Idempotent.
- **Empty days/regions:** LIST returns empty. No error, no cost beyond the API call.
- **History cap:** Not populated, so the 10k cap and time-window fallback are never triggered.
- **First sync after upgrade:** Migration reads max timestamp from old history. Safe even if history is at the 10k cap.
- **Non-CloudTrail connections:** `flatten_records_key` not set = entire codepath is skipped. Zero regression.
- **Region discovery caching:** One API call per sync. Regions don't change, but re-discovering is cheap insurance.

## Testing & Validation

### Unit Tests
- Prefix generation: given start_date + regions + today → correct list of prefixes
- Cursor: high-water mark advances correctly, `_should_sync_file` filters correctly
- Migration: old state with populated history → extracts max timestamp → new format
- Edge cases: empty history, single region, same-day cursor

### Benchmark with Real Data
- List Forter's us-east-1 for 3 days using new parallel approach vs current broad prefix
- Measure: time to list, number of API calls, number of files returned
- Expected: seconds vs minutes

### Integration
- Run a sync against test tenant with CloudTrail data
- Verify: files listed correctly, cursor state saved correctly, incremental sync only processes new files

## Out of Scope

- Changes to the Airbyte destination (Snowflake writes)
- Changes to CDK internals (ConcurrentSource, thread pool)
- Multi-process parallelism for parsing (proven unnecessary — parsing is not the bottleneck)
- Non-CloudTrail S3 sources (they use the existing listing path unchanged)
