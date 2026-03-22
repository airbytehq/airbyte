# S3 CloudTrail Parser Optimization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the inefficient JSONL parser + FlattenableFileBasedStream pipeline with a purpose-built `JsonFlattenParser` that reads CloudTrail files in one shot and yields individual events directly.

**Architecture:** New `JsonFlattenParser` reads whole file, one `orjson.loads()`, yields each event wrapped as `{"data": event}` (matching existing Snowflake schema). Swapped in via `_make_default_stream()` when `flatten_records_key` is set. `FlattenableFileBasedStream` deleted.

**Tech Stack:** Python, orjson, Airbyte CDK FileTypeParser, pytest

**Spec:** `docs/superpowers/specs/2026-03-22-s3-cloudtrail-parser-optimization-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `source_s3/v4/parsers/json_flatten_parser.py` | **Create** | `JsonFlattenParser` — reads JSON file, extracts array under configured key, yields individual records |
| `source_s3/v4/source.py` | **Modify** | Swap parser in `_make_default_stream()`, remove `FlattenableFileBasedStream` usage |
| `source_s3/v4/flattenable_stream.py` | **Delete** | No longer needed |
| `unit_tests/v4/test_json_flatten_parser.py` | **Create** | Unit tests for the new parser |

All paths below are relative to: `/Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3/`

---

### Task 1: Create `JsonFlattenParser` with tests

**Files:**
- Create: `source_s3/v4/parsers/json_flatten_parser.py`
- Create: `unit_tests/v4/test_json_flatten_parser.py`

- [ ] **Step 1: Write the failing tests**

Create `unit_tests/v4/test_json_flatten_parser.py`:

```python
import logging
from io import StringIO
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import orjson
import pytest

from source_s3.v4.parsers.json_flatten_parser import JsonFlattenParser


class FakeRemoteFile:
    def __init__(self, uri: str):
        self.uri = uri
        self.last_modified = None


class FakeStreamReader:
    """Simulates stream_reader.open_file() returning a file-like object."""

    def __init__(self, content: str):
        self._content = content

    def open_file(self, file, mode, encoding, logger):
        return StringIO(self._content)


def _collect_records(parser, content: str, file_uri: str = "test.json") -> List[Dict[str, Any]]:
    """Helper to run parse_records and collect all yielded records."""
    reader = FakeStreamReader(content)
    file = FakeRemoteFile(file_uri)
    config = MagicMock()
    logger = logging.getLogger("test")
    return list(parser.parse_records(config, file, reader, logger, None))


class TestJsonFlattenParserParseRecords:
    def test_yields_individual_records_wrapped_in_data(self):
        """Each element under the flatten key is wrapped as {"data": event}."""
        content = orjson.dumps({"Records": [{"a": 1}, {"b": 2}, {"c": 3}]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [{"data": {"a": 1}}, {"data": {"b": 2}}, {"data": {"c": 3}}]

    def test_single_record(self):
        content = orjson.dumps({"Records": [{"only": "one"}]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [{"data": {"only": "one"}}]

    def test_empty_array_yields_nothing(self):
        content = orjson.dumps({"Records": []}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == []

    def test_missing_key_yields_nothing_and_warns(self, caplog):
        content = orjson.dumps({"Other": [{"a": 1}]}).decode()
        parser = JsonFlattenParser("Records")
        with caplog.at_level(logging.WARNING):
            records = _collect_records(parser, content)
        assert records == []
        assert "not found" in caplog.text

    def test_malformed_json_raises_record_parse_error(self):
        from airbyte_cdk.sources.file_based.exceptions import RecordParseError

        parser = JsonFlattenParser("Records")
        with pytest.raises(RecordParseError):
            _collect_records(parser, "not valid json {{{")

    def test_preserves_nested_event_structure(self):
        event = {
            "eventVersion": "1.08",
            "userIdentity": {"type": "AssumedRole", "arn": "arn:aws:iam::123:role/x"},
            "sourceIPAddress": "10.0.0.1",
            "requestParameters": {"bucketName": "b", "key": "k"},
        }
        content = orjson.dumps({"Records": [event]}).decode()
        parser = JsonFlattenParser("Records")
        records = _collect_records(parser, content)
        assert records == [{"data": event}]

    def test_custom_flatten_key(self):
        content = orjson.dumps({"events": [{"x": 1}]}).decode()
        parser = JsonFlattenParser("events")
        records = _collect_records(parser, content)
        assert records == [{"data": {"x": 1}}]


class TestJsonFlattenParserConfig:
    def test_check_config_returns_true(self):
        parser = JsonFlattenParser("Records")
        ok, err = parser.check_config(MagicMock())
        assert ok is True
        assert err is None

    def test_file_read_mode_is_read(self):
        from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode

        parser = JsonFlattenParser("Records")
        assert parser.file_read_mode == FileReadMode.READ
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
# Use the vault venv which has the CDK installed
/Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-vault/.venv/bin/python -m pytest unit_tests/v4/test_json_flatten_parser.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'source_s3.v4.parsers.json_flatten_parser'`

- [ ] **Step 3: Write the `JsonFlattenParser` implementation**

Create `source_s3/v4/parsers/json_flatten_parser.py`:

```python
import logging
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import orjson

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType, schemaless_schema


class JsonFlattenParser(FileTypeParser):
    """
    Parser for JSON files containing a single object with a top-level array key.
    Reads the entire file in one shot, parses with a single orjson.loads() call,
    and yields each element of the array individually.

    Designed for CloudTrail logs: {"Records": [{event1}, {event2}, ...]}
    Each event becomes a separate Airbyte record (one Snowflake row).
    """

    ENCODING = "utf8"

    def __init__(self, flatten_key: str):
        self.flatten_key = flatten_key

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        return True, None

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        """No-op — this parser is used with schemaless streams (raw VARIANT ingestion)."""
        return schemaless_schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
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
                yield {"data": record}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
PYTHONPATH=. /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-vault/.venv/bin/python -m pytest unit_tests/v4/test_json_flatten_parser.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add source_s3/v4/parsers/json_flatten_parser.py unit_tests/v4/test_json_flatten_parser.py
git commit -m "feat: add JsonFlattenParser for efficient CloudTrail ingestion"
```

---

### Task 2: Wire up `JsonFlattenParser` in `SourceS3` and remove `FlattenableFileBasedStream`

**Files:**
- Modify: `source_s3/v4/source.py` (lines 46, 66-87)
- Delete: `source_s3/v4/flattenable_stream.py`

- [ ] **Step 1: Modify `source.py` to use `JsonFlattenParser`**

In `source_s3/v4/source.py`, make these changes:

**Replace the import** (line 46):
```python
# REMOVE this line:
from source_s3.v4.flattenable_stream import FlattenableFileBasedStream

# ADD these imports:
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import DefaultFileBasedStream
from source_s3.v4.parsers.json_flatten_parser import JsonFlattenParser
```

**Replace `_make_default_stream`** (lines 66-87):
```python
    def _make_default_stream(
        self,
        stream_config: FileBasedStreamConfig,
        cursor: Optional[AbstractFileBasedCursor],
        parsed_config: AbstractFileBasedSpec,
    ) -> AbstractFileBasedStream:
        flatten_records_key = getattr(parsed_config, 'flatten_records_key', None)
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
            use_file_transfer=use_file_transfer(parsed_config),
            preserve_directory_structure=preserve_directory_structure(parsed_config),
        )
```

- [ ] **Step 2: Delete `flattenable_stream.py`**

```bash
rm source_s3/v4/flattenable_stream.py
```

- [ ] **Step 3: Run existing tests to verify nothing breaks**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
PYTHONPATH=. /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-vault/.venv/bin/python -m pytest unit_tests/ -v --tb=short 2>&1 | tail -30
```

Expected: All tests pass. No references to `FlattenableFileBasedStream` in any test files (confirmed during spec review).

- [ ] **Step 4: Verify no dangling imports**

```bash
grep -rn "flattenable_stream\|FlattenableFileBasedStream" source_s3/ unit_tests/
```

Expected: No matches.

- [ ] **Step 5: Commit**

```bash
git add source_s3/v4/source.py unit_tests/
git rm source_s3/v4/flattenable_stream.py
git commit -m "refactor: replace FlattenableFileBasedStream with JsonFlattenParser

Swap in JsonFlattenParser when flatten_records_key is configured.
Delete FlattenableFileBasedStream (139 lines) — no longer needed."
```

---

### Task 3: Benchmark before/after

**Files:**
- Create: `benchmarks/benchmark_flatten.py` (temporary, not committed)

- [ ] **Step 1: Write the benchmark script**

Create `benchmarks/benchmark_flatten.py`:

```python
"""
Benchmark: old pipeline (JsonlParser + FlattenableFileBasedStream) vs new (JsonFlattenParser).

Usage:
    PYTHONPATH=. python benchmarks/benchmark_flatten.py
"""

import json
import time
from io import StringIO
from unittest.mock import MagicMock

import orjson

from source_s3.v4.parsers.json_flatten_parser import JsonFlattenParser


def generate_cloudtrail(n_records: int) -> str:
    records = []
    for i in range(n_records):
        records.append({
            "eventVersion": "1.08",
            "userIdentity": {
                "type": "AssumedRole",
                "principalId": f"AROA3XFRBF23:user-{i}",
                "arn": f"arn:aws:sts::123456789012:assumed-role/role-{i}/session",
                "accountId": "123456789012",
            },
            "eventTime": f"2026-01-01T00:{i % 60:02d}:00Z",
            "eventSource": "s3.amazonaws.com",
            "eventName": "GetObject",
            "sourceIPAddress": f"10.0.{i % 256}.{i % 256}",
            "requestParameters": {"bucketName": "bucket", "key": f"obj-{i}.json"},
        })
    return orjson.dumps({"Records": records}).decode()


class FakeFile:
    def __init__(self, uri):
        self.uri = uri
        self.last_modified = None


class FakeReader:
    def __init__(self, content):
        self._content = content

    def open_file(self, file, mode, encoding, logger):
        return StringIO(self._content)


def benchmark_new_parser(content, n_iterations=5):
    """Benchmark JsonFlattenParser."""
    parser = JsonFlattenParser("Records")
    reader = FakeReader(content)
    file = FakeFile("cloudtrail.json")
    logger = MagicMock()
    config = MagicMock()

    times = []
    for _ in range(n_iterations):
        start = time.perf_counter()
        count = sum(1 for _ in parser.parse_records(config, file, reader, logger, None))
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg = sum(times) / len(times)
    return avg, count


def benchmark_jsonl_accumulator(content, n_iterations=5):
    """Simulate the old JSONL parser's line-by-line accumulator behavior."""
    times = []
    count = 0
    for _ in range(n_iterations):
        start = time.perf_counter()
        # Simulate JSONL parser: line-by-line with accumulator
        accumulator = ""
        parsed = None
        for line in content.split("\n"):
            accumulator += line + "\n"
            try:
                parsed = orjson.loads(accumulator)
            except orjson.JSONDecodeError:
                pass
        # Then flatten
        if parsed:
            records = parsed.get("Records", [])
            count = 0
            for r in records:
                data = {"data": r}
                count += 1
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg = sum(times) / len(times)
    return avg, count


if __name__ == "__main__":
    for n in [1000, 10000, 50000]:
        content = generate_cloudtrail(n)
        size_mb = len(content.encode()) / 1024 / 1024

        print(f"\n{'='*60}")
        print(f"{n} records ({size_mb:.1f} MB)")
        print(f"{'='*60}")

        old_avg, old_count = benchmark_jsonl_accumulator(content)
        new_avg, new_count = benchmark_new_parser(content)

        print(f"OLD (JSONL accumulator): {old_avg*1000:.1f}ms  ({old_count} records)")
        print(f"NEW (JsonFlattenParser): {new_avg*1000:.1f}ms  ({new_count} records)")
        print(f"Speedup: {old_avg/new_avg:.1f}x")
```

- [ ] **Step 2: Run the benchmark**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
PYTHONPATH=. /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-vault/.venv/bin/python benchmarks/benchmark_flatten.py
```

Expected: New parser is significantly faster (the accumulator does N-1 failed `orjson.loads` calls). Record the speedup numbers.

- [ ] **Step 3: Clean up benchmark file (do not commit)**

```bash
rm -rf benchmarks/
```

---

### Task 4: Update spec status and commit

**Files:**
- Modify: `docs/superpowers/specs/2026-03-22-s3-cloudtrail-parser-optimization-design.md`

- [ ] **Step 1: Update spec status to Complete**

Change `**Status:** Draft` to `**Status:** Complete` in the spec file.

- [ ] **Step 2: Add benchmark results to spec**

Append the actual benchmark numbers from Task 3 to the "Benchmark (before/after)" section of the spec.

- [ ] **Step 3: Final commit**

```bash
git add docs/superpowers/specs/2026-03-22-s3-cloudtrail-parser-optimization-design.md
git commit -m "docs: mark CloudTrail parser optimization spec as complete with benchmark results"
```
