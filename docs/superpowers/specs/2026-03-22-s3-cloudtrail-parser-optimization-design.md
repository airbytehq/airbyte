# S3 CloudTrail Parser Optimization

**Date:** 2026-03-22
**Status:** Draft

## Problem

The Airbyte source-s3 connector ingests CloudTrail JSON files through an inefficient pipeline:

1. **JSONL parser line-by-line accumulator:** CloudTrail files are single JSON objects, not JSONL. The CDK's `JsonlParser` reads line by line, trying `orjson.loads()` on every accumulated line. For a file with N lines, this produces N-1 failed parse attempts before the final line completes the object. The CDK itself warns: *"Performance could be greatly reduced"* for multiline JSON.

2. **FlattenableFileBasedStream indirection:** After the parser yields one giant dict, `FlattenableFileBasedStream` extracts the `Records` array and re-yields each event wrapped as `{"data": event}`. This adds an unnecessary abstraction layer between parsing and record emission.

3. **Single-core GIL bottleneck:** JSON parsing is CPU-bound. The CDK uses threads (not processes) for concurrent file processing, so the GIL serializes all parsing to one core. Reducing per-file CPU waste is the most impactful improvement within the current architecture.

Benchmarking confirmed that `orjson.loads` consumes ~87% of pipeline CPU time, and the CDK already uses `orjson` — so the parser library isn't the issue. The waste is in how it's called.

## CloudTrail File Format

```json
{"Records": [{event1}, {event2}, ..., {eventN}]}
```

- Single JSON object with one key (`Records`) containing an array of event dicts
- Files are typically gzipped (`.json.gz`), decompressed by smart_open before the parser sees them
- Each event must become one Snowflake row (VARIANT column) because Snowflake has a 16MB uncompressed limit per VARIANT value — the full `Records` array can exceed this

## Design

### New: `JsonFlattenParser`

A parser that reads the entire file in one shot, parses it with a single `orjson.loads()` call, and yields each record under the configured key individually.

```python
class JsonFlattenParser(FileTypeParser):
    ENCODING = "utf8"

    def __init__(self, flatten_key: str):
        self.flatten_key = flatten_key

    def check_config(self, config) -> Tuple[bool, Optional[str]]:
        return True, None

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    async def infer_schema(self, config, file, stream_reader, logger) -> SchemaType:
        """No-op — this parser is used with schemaless streams (raw VARIANT ingestion)."""
        return schemaless_schema

    def parse_records(self, config, file, stream_reader, logger, schema):
        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            try:
                content = fp.read()
                data = orjson.loads(content)
            except orjson.JSONDecodeError:
                raise RecordParseError(
                    FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri
                )
            if self.flatten_key not in data:
                logger.warning(f"Key '{self.flatten_key}' not found in {file.uri}, skipping")
                return
            records = data[self.flatten_key]
            if not records:
                logger.info(f"Empty '{self.flatten_key}' array in {file.uri}")
                return
            for record in records:
                yield {"data": record}  # Wraps here to match existing Snowflake schema, independent of schemaless config
```

Key properties:
- `fp.read()` — reads entire file at once, no line-by-line accumulation
- One `orjson.loads()` — zero failed parse retries
- **Yields `{"data": record}` directly** — matches the existing `FlattenableFileBasedStream` output, independent of the `schemaless` config flag
- Error handling: raises `RecordParseError` on malformed JSON for consistent CDK error reporting
- Distinguishes missing key (warning) from empty array (info) for operational observability
- Decompression is handled upstream by smart_open — this parser only sees the decompressed stream
- Schema inference is a no-op returning `schemaless_schema` — the stream is always schemaless (raw VARIANT ingestion), so inference is never called in practice
- Implements all `FileTypeParser` abstract methods: `check_config`, `file_read_mode`, `infer_schema`, `parse_records`

**Memory note:** `fp.read()` + `orjson.loads()` holds ~2x the decompressed file size in memory. This is fine for typical CloudTrail files (a few MB). If files ever reach hundreds of MB, a streaming parser (e.g., `ijson`) could be considered, but that's out of scope.

### Integration Point

The parser swap happens in `SourceS3._make_default_stream()`. The current override has a **pre-existing signature mismatch** with the parent class — it accepts `parsed_config` where the parent expects `use_file_transfer`. This is fixed as part of the change: `flatten_records_key` is read from `self.main_config` (already stored by the existing `_get_parsed_config` override), and the method signature is corrected to match the parent.

- If `flatten_records_key` is set: create a **per-stream copy** of the parsers dict with `JsonFlattenParser(flatten_key)` overriding the `JsonlFormat` entry. Return a standard `DefaultFileBasedStream` with this modified parsers dict. The shared `self.parsers` is never mutated.
- If `flatten_records_key` is NOT set: current behavior, unchanged. JSONL parser + `DefaultFileBasedStream`.

```python
def _make_default_stream(self, stream_config, cursor, use_file_transfer=False):
    flatten_records_key = getattr(self.main_config, 'flatten_records_key', None)
    if flatten_records_key:
        parsers = {**self.parsers, JsonlFormat: JsonFlattenParser(flatten_records_key)}
    else:
        parsers = self.parsers
    return DefaultFileBasedStream(
        config=stream_config,
        catalog_schema=self.stream_schemas.get(stream_config.name),
        stream_reader=self.stream_reader,
        availability_strategy=self.availability_strategy,
        discovery_policy=self.discovery_policy,
        parsers=parsers,
        validation_policy=self._validate_and_get_validation_policy(stream_config),
        errors_collector=self.errors_collector,
        cursor=cursor,
        use_file_transfer=use_file_transfer,
    )
```

This preserves backward compatibility — existing Airbyte connections with `flatten_records_key` configured work without any config changes. They just get faster.

### Removed: `FlattenableFileBasedStream`

The entire `FlattenableFileBasedStream` class (139 lines) is deleted. Its only purpose was to extract the flatten key's array after the JSONL parser yielded the whole object. With `JsonFlattenParser` yielding individual records directly, `DefaultFileBasedStream` handles everything.

### Data Flow Comparison

```
BEFORE:
  File -> smart_open (decompress)
       -> JsonlParser (line-by-line, N-1 failed orjson.loads, 1 success)
       -> yields 1 giant dict
       -> FlattenableFileBasedStream.read_records_from_slice()
       -> extracts Records array, wraps each as {"data": event}
       -> AirbyteMessage per event
       -> Snowflake row

AFTER:
  File -> smart_open (decompress)
       -> JsonFlattenParser (fp.read(), 1 orjson.loads)
       -> yields {"data": event} per record
       -> DefaultFileBasedStream.read_records_from_slice()
       -> AirbyteMessage per event
       -> Snowflake row
```

### Files Changed

| File | Action |
|------|--------|
| `source_s3/v4/parsers/json_flatten_parser.py` | **Create** — `JsonFlattenParser` class |
| `source_s3/v4/source.py` | **Modify** — parser swap logic in `_make_default_stream()`, remove `FlattenableFileBasedStream` import |
| `source_s3/v4/flattenable_stream.py` | **Delete** |
| `unit_tests/v4/test_json_flatten_parser.py` | **Create** — unit tests for the new parser |

### Config

The `flatten_records_key` field on `Config` stays unchanged. It serves as both:
- The trigger for parser selection (set = use `JsonFlattenParser`, unset = use `JsonlParser`)
- The key name passed to the parser

No new config fields. No changes to existing Airbyte connection configurations.

## Testing & Validation

### Benchmark (before/after)

Run a benchmark comparing the old pipeline (JSONL parser + FlattenableFileBasedStream) against the new pipeline (JsonFlattenParser) on synthetic CloudTrail data:

- Generate synthetic data at multiple sizes (1k, 10k, 50k records)
- Measure: total time, records/sec, CPU profile breakdown
- The primary metric is records/sec improvement

### Output Parity

Run both old and new code paths on the same input and verify identical output:
- Record shape: `{"data": event_dict}` with `_ab_source_file_last_modified` and `_ab_source_file_url` metadata
- Record count: same number of events yielded
- Record content: byte-identical event dicts

### Edge Cases

- Empty `Records` array — should yield zero records, no error
- Missing flatten key — should log warning, yield zero records
- Single-record file — should yield exactly one record
- `flatten_records_key` not set — should fall back to normal JSONL parser path unchanged

### Integration

Run a sync against the test tenant's CloudTrail S3 source and verify:
- Rows land in Snowflake identically to the current pipeline
- Sync completes successfully
- Compare sync duration to previous runs

## Out of Scope

- Multi-core parallelism (multiprocessing) — the GIL limitation remains, but per-file waste is drastically reduced
- Upstream Airbyte merge (v4.15.2 / CDK v7) — separate effort, no performance gains identified
- `faster_boto3` — benchmarking showed the bottleneck is CPU parsing, not HTTP overhead
- Decompression optimization — handled by smart_open, not our layer
