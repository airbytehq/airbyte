# S3 CloudTrail Listing & Cursor Optimization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broad S3 file listing (1.5-3 hours for 35M files) with date-aware parallel prefix listing (seconds), and replace the 10k-entry filename cursor with a simple high-water timestamp.

**Architecture:** When `flatten_records_key` is set (CloudTrail mode), `get_matching_files()` generates per-day S3 prefixes from the cursor date to today and lists them in parallel. The cursor stores a single `cloudtrail_cursor` timestamp. State is bridged from cursor to reader via `SourceS3.streams()` override.

**Tech Stack:** Python, boto3, ThreadPoolExecutor, pytest

**Spec:** `docs/superpowers/specs/2026-03-22-s3-cloudtrail-listing-cursor-optimization-design.md`

**Branch:** `feat/cloudtrail-listing-cursor-optimization`

All paths relative to: `/Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3/`

Poetry venv: `$(poetry env info --path)/bin/python`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `source_s3/v4/cursor.py` | **Modify** | Add CloudTrail cursor mode: `cloudtrail_cursor` field, override `_should_sync_file`, `add_file`, `_get_cursor`, `get_state`, `set_initial_state` |
| `source_s3/v4/stream_reader.py` | **Modify** | Add `_cloudtrail_cursor_date`, `set_cloudtrail_cursor_date()`, `_discover_cloudtrail_regions()`, `_generate_cloudtrail_prefixes()`, CloudTrail-aware `get_matching_files()` |
| `source_s3/v4/source.py` | **Modify** | Override `streams()` to bridge cursor state to reader |
| `source_s3/v4/config.py` | **Modify** | Add optional `cloudtrail_regions` field |
| `unit_tests/v4/test_cloudtrail_cursor.py` | **Create** | Tests for CloudTrail cursor |
| `unit_tests/v4/test_cloudtrail_listing.py` | **Create** | Tests for date-aware listing |

---

### Task 1: CloudTrail Cursor

**Files:**
- Modify: `source_s3/v4/cursor.py`
- Create: `unit_tests/v4/test_cloudtrail_cursor.py`

- [ ] **Step 1: Write cursor tests**

Create `unit_tests/v4/test_cloudtrail_cursor.py`:

```python
import logging
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from source_s3.v4.cursor import Cursor


def _make_cursor(flatten_records_key="Records"):
    stream_config = MagicMock()
    stream_config.days_to_sync_if_history_is_full = 3
    cursor = Cursor(stream_config, flatten_records_key=flatten_records_key)
    return cursor


def _make_file(uri: str, last_modified: datetime) -> RemoteFile:
    return RemoteFile(uri=uri, last_modified=last_modified)


class TestCloudTrailCursorMode:
    def test_cloudtrail_mode_enabled(self):
        cursor = _make_cursor(flatten_records_key="Records")
        assert cursor._cloudtrail_mode is True

    def test_cloudtrail_mode_disabled_when_no_key(self):
        cursor = _make_cursor(flatten_records_key=None)
        assert cursor._cloudtrail_mode is False

    def test_initial_state_no_cloudtrail_cursor(self):
        """First sync after upgrade: no cloudtrail_cursor, falls back to None."""
        cursor = _make_cursor()
        cursor.set_initial_state({"history": {"file.json": "2026-01-01T00:00:00.000000Z"}})
        assert cursor._cloudtrail_cursor_dt is None

    def test_initial_state_with_cloudtrail_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({
            "history": {},
            "cloudtrail_cursor": "2026-03-20T10:00:00.000000Z",
        })
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 20, 10, 0, 0)

    def test_should_sync_file_newer_than_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("new.json", datetime(2026, 3, 21, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is True

    def test_should_not_sync_file_older_than_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("old.json", datetime(2026, 3, 19, 5, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_should_not_sync_file_equal_to_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        file = _make_file("same.json", datetime(2026, 3, 20, 10, 0, 0))
        assert cursor._should_sync_file(file, logging.getLogger()) is False

    def test_add_file_advances_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 21, 5, 0, 0)

    def test_add_file_does_not_regress_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-21T10:00:00.000000Z"})
        cursor.add_file(_make_file("old.json", datetime(2026, 3, 20, 5, 0, 0)))
        assert cursor._cloudtrail_cursor_dt == datetime(2026, 3, 21, 10, 0, 0)

    def test_add_file_does_not_populate_history(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        assert cursor._file_to_datetime_history == {}

    def test_get_state_includes_cloudtrail_cursor(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        cursor.add_file(_make_file("new.json", datetime(2026, 3, 21, 5, 0, 0)))
        state = cursor.get_state()
        assert state["cloudtrail_cursor"] == "2026-03-21T05:00:00.000000Z"
        assert state["history"] == {}

    def test_get_cursor_returns_cloudtrail_cursor_for_ui(self):
        cursor = _make_cursor()
        cursor.set_initial_state({"cloudtrail_cursor": "2026-03-20T10:00:00.000000Z"})
        state = cursor.get_state()
        assert state[DefaultFileBasedCursor.CURSOR_FIELD] is not None

    def test_non_cloudtrail_mode_delegates_to_super(self):
        """When flatten_records_key is None, cursor behaves as default."""
        cursor = _make_cursor(flatten_records_key=None)
        cursor.set_initial_state({})
        file = _make_file("any.json", datetime(2026, 3, 21, 5, 0, 0))
        # Default cursor with empty history syncs everything
        assert cursor._should_sync_file(file, logging.getLogger()) is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/v4/test_cloudtrail_cursor.py -v 2>&1 | tail -20
```

Expected: FAIL (Cursor doesn't accept `flatten_records_key` yet)

- [ ] **Step 3: Implement CloudTrail cursor mode**

Modify `source_s3/v4/cursor.py`. Add `flatten_records_key` parameter to `__init__`, add `_cloudtrail_mode` flag, override methods when in CloudTrail mode:

```python
# In Cursor.__init__, add flatten_records_key parameter:
def __init__(self, stream_config: FileBasedStreamConfig, flatten_records_key: str = None, **_: Any):
    super().__init__(stream_config)
    self._running_migration = False
    self._v3_migration_start_datetime = None
    self._cloudtrail_mode = bool(flatten_records_key)
    self._cloudtrail_cursor_dt: Optional[datetime] = None

# Override set_initial_state to handle cloudtrail_cursor:
def set_initial_state(self, value: StreamState) -> None:
    if self._cloudtrail_mode and "cloudtrail_cursor" in value:
        self._cloudtrail_cursor_dt = datetime.strptime(
            value["cloudtrail_cursor"], DefaultFileBasedCursor.DATE_TIME_FORMAT
        )
    # Always call parent for v3 migration and history handling
    if self._is_legacy_state(value):
        self._running_migration = True
        value = self._convert_legacy_state(value)
    else:
        self._running_migration = False
    self._v3_migration_start_datetime = (
        datetime.strptime(value.get(Cursor._V3_MIN_SYNC_DATE_FIELD), DefaultFileBasedCursor.DATE_TIME_FORMAT)
        if Cursor._V3_MIN_SYNC_DATE_FIELD in value
        else None
    )
    super().set_initial_state(value)

# Override _should_sync_file for CloudTrail mode:
def _should_sync_file(self, file: RemoteFile, logger: logging.Logger) -> bool:
    if self._cloudtrail_mode and self._cloudtrail_cursor_dt is not None:
        return file.last_modified > self._cloudtrail_cursor_dt
    # Non-CloudTrail: existing logic
    if self._v3_migration_start_datetime and file.last_modified < self._v3_migration_start_datetime:
        return False
    elif self._running_migration:
        return True
    else:
        return super()._should_sync_file(file, logger)

# Override add_file for CloudTrail mode:
def add_file(self, file: RemoteFile) -> None:
    if self._cloudtrail_mode:
        if self._cloudtrail_cursor_dt is None or file.last_modified > self._cloudtrail_cursor_dt:
            self._cloudtrail_cursor_dt = file.last_modified
        return  # Do NOT call super — skip history population
    super().add_file(file)

# Override get_state to include cloudtrail_cursor:
def get_state(self) -> StreamState:
    if self._cloudtrail_mode:
        cursor_str = (
            self._cloudtrail_cursor_dt.strftime(DefaultFileBasedCursor.DATE_TIME_FORMAT)
            if self._cloudtrail_cursor_dt
            else None
        )
        return {
            "history": {},
            self.CURSOR_FIELD: cursor_str,
            "cloudtrail_cursor": cursor_str,
        }
    # Non-CloudTrail: existing logic
    state = {"history": self._file_to_datetime_history, self.CURSOR_FIELD: self._get_cursor()}
    if self._v3_migration_start_datetime:
        return {
            **state,
            Cursor._V3_MIN_SYNC_DATE_FIELD: datetime.strftime(
                self._v3_migration_start_datetime, DefaultFileBasedCursor.DATE_TIME_FORMAT
            ),
        }
    return state
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/v4/test_cloudtrail_cursor.py -v
```

Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add source_s3/v4/cursor.py unit_tests/v4/test_cloudtrail_cursor.py
git commit -m "feat: add CloudTrail cursor mode with high-water timestamp

When flatten_records_key is set, cursor uses a single cloudtrail_cursor
timestamp instead of the 10k-entry filename history dict.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Date-Aware Prefix Listing

**Files:**
- Modify: `source_s3/v4/stream_reader.py`
- Create: `unit_tests/v4/test_cloudtrail_listing.py`

- [ ] **Step 1: Write listing tests**

Create `unit_tests/v4/test_cloudtrail_listing.py`:

```python
import logging
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

import pytest
import pytz

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_s3.v4.stream_reader import SourceS3StreamReader


class TestGenerateCloudTrailPrefixes:
    def test_generates_daily_prefixes_for_each_region(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1", "eu-west-1"],
            start_date=date(2026, 3, 20),
            end_date=date(2026, 3, 22),
        )
        expected = [
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/20/",
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/21/",
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/22/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/20/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/21/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/22/",
        ]
        assert sorted(prefixes) == sorted(expected)

    def test_single_day(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1"],
            start_date=date(2026, 3, 22),
            end_date=date(2026, 3, 22),
        )
        assert prefixes == ["AWSLogs/123/CloudTrail/us-east-1/2026/03/22/"]

    def test_cross_month_boundary(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1"],
            start_date=date(2026, 2, 28),
            end_date=date(2026, 3, 1),
        )
        assert len(prefixes) == 2
        assert "AWSLogs/123/CloudTrail/us-east-1/2026/02/28/" in prefixes
        assert "AWSLogs/123/CloudTrail/us-east-1/2026/03/01/" in prefixes


class TestExtractCloudTrailBasePrefix:
    def test_extracts_from_globs(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(
            ["AWSLogs/174522763890/CloudTrail/**/*.json.gz"]
        )
        assert prefix == "AWSLogs/174522763890/CloudTrail/"

    def test_extracts_from_prefix_with_trailing_slash(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(
            ["AWSLogs/174522763890/CloudTrail/us-east-1/**"]
        )
        assert prefix == "AWSLogs/174522763890/CloudTrail/"

    def test_returns_none_if_no_cloudtrail(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(["data/**/*.csv"])
        assert prefix is None


class TestDiscoverCloudTrailRegions:
    def test_discovers_regions_from_s3(self):
        reader = SourceS3StreamReader()
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            "CommonPrefixes": [
                {"Prefix": "AWSLogs/123/CloudTrail/us-east-1/"},
                {"Prefix": "AWSLogs/123/CloudTrail/eu-west-1/"},
                {"Prefix": "AWSLogs/123/CloudTrail/ap-northeast-1/"},
            ]
        }
        regions = reader._discover_cloudtrail_regions(mock_s3, "bucket", "AWSLogs/123/CloudTrail/")
        assert regions == ["us-east-1", "eu-west-1", "ap-northeast-1"]

    def test_empty_bucket_returns_empty(self):
        reader = SourceS3StreamReader()
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {}
        regions = reader._discover_cloudtrail_regions(mock_s3, "bucket", "AWSLogs/123/CloudTrail/")
        assert regions == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/v4/test_cloudtrail_listing.py -v 2>&1 | tail -20
```

Expected: FAIL (methods don't exist yet)

- [ ] **Step 3: Implement date-aware listing**

Modify `source_s3/v4/stream_reader.py`. Add to `SourceS3StreamReader`:

```python
# Add imports at top of file:
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

# Add to __init__:
def __init__(self):
    super().__init__()
    self._s3_client = None
    self._cloudtrail_cursor_date: Optional[datetime] = None

# Add new methods:
def set_cloudtrail_cursor_date(self, cursor_date: Optional[datetime]) -> None:
    self._cloudtrail_cursor_date = cursor_date

def _extract_cloudtrail_base_prefix(self, globs: List[str]) -> Optional[str]:
    """Extract the CloudTrail base prefix (up to and including 'CloudTrail/') from globs."""
    for glob in globs:
        match = re.match(r"(.*CloudTrail/)", glob)
        if match:
            return match.group(1)
    return None

def _discover_cloudtrail_regions(
    self, s3: BaseClient, bucket: str, base_prefix: str
) -> List[str]:
    """Discover CloudTrail regions via delimiter-based listing (one API call)."""
    response = s3.list_objects_v2(Bucket=bucket, Prefix=base_prefix, Delimiter="/")
    regions = []
    for prefix_obj in response.get("CommonPrefixes", []):
        # prefix_obj["Prefix"] is like "AWSLogs/123/CloudTrail/us-east-1/"
        region = prefix_obj["Prefix"][len(base_prefix):].strip("/")
        if region:
            regions.append(region)
    return regions

def _generate_cloudtrail_prefixes(
    self,
    base_prefix: str,
    regions: List[str],
    start_date: date,
    end_date: date,
) -> List[str]:
    """Generate per-day S3 prefixes for each region."""
    prefixes = []
    current = start_date
    while current <= end_date:
        date_path = current.strftime("%Y/%m/%d")
        for region in regions:
            prefixes.append(f"{base_prefix}{region}/{date_path}/")
        current += timedelta(days=1)
    return prefixes

def _list_cloudtrail_prefix(
    self, s3: BaseClient, bucket: str, prefix: str, globs: List[str], logger: logging.Logger
) -> List[RemoteFile]:
    """List all files under a single prefix. Called from thread pool."""
    files = []
    kwargs = {"Bucket": bucket, "Prefix": prefix}
    while True:
        response = s3.list_objects_v2(**kwargs)
        for obj in response.get("Contents", []):
            if self._is_folder(obj):
                continue
            remote_file = self._handle_regular_file(obj)
            if self.file_matches_globs(remote_file, globs):
                files.append(remote_file)
        if next_token := response.get("NextContinuationToken"):
            kwargs["ContinuationToken"] = next_token
        else:
            break
    return files

# Modify get_matching_files to use CloudTrail optimization:
def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
    # Check if CloudTrail optimization applies
    if self.config.flatten_records_key:
        base_prefix = self._extract_cloudtrail_base_prefix(globs)
        if base_prefix:
            yield from self._get_matching_files_cloudtrail(globs, base_prefix, logger)
            return

    # Default path: existing behavior
    s3 = self.s3_client
    prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs)
    seen = set()
    total_n_keys = 0
    try:
        for current_prefix in prefixes if prefixes else [None]:
            for remote_file in self._page(s3, globs, self.config.bucket, current_prefix, seen, logger):
                total_n_keys += 1
                yield remote_file
        logger.info(f"Finished listing objects from S3. Found {total_n_keys} objects total ({len(seen)} unique objects).")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchBucket":
            raise CustomFileBasedException(
                f"The bucket {self.config.bucket} does not exist.", failure_type=FailureType.config_error, exception=exc
            )
        self._raise_error_listing_files(globs, exc)
    except Exception as exc:
        self._raise_error_listing_files(globs, exc)

def _get_matching_files_cloudtrail(
    self, globs: List[str], base_prefix: str, logger: logging.Logger
) -> Iterable[RemoteFile]:
    """CloudTrail-optimized listing: date-aware prefixes, parallel threads."""
    import pendulum
    from datetime import date as date_type

    s3 = self.s3_client
    bucket = self.config.bucket

    # Determine start date
    if self._cloudtrail_cursor_date:
        start_dt = self._cloudtrail_cursor_date - timedelta(days=1)  # overlap buffer
        start = start_dt.date() if isinstance(start_dt, datetime) else start_dt
    elif self.config.start_date:
        start = pendulum.parse(self.config.start_date).date()
    else:
        logger.warning("CloudTrail mode: no cursor or start_date, falling back to broad listing")
        yield from self._get_matching_files_default(globs, base_prefix, logger)
        return

    end = date_type.today()

    # Discover or use configured regions
    if hasattr(self.config, 'cloudtrail_regions') and self.config.cloudtrail_regions:
        regions = self.config.cloudtrail_regions
    else:
        regions = self._discover_cloudtrail_regions(s3, bucket, base_prefix)

    if not regions:
        logger.warning(f"No CloudTrail regions found under {base_prefix}")
        return

    logger.info(f"CloudTrail listing: {len(regions)} regions, {start} to {end}")

    # Generate per-day prefixes
    prefixes = self._generate_cloudtrail_prefixes(base_prefix, regions, start, end)
    logger.info(f"Generated {len(prefixes)} day-prefixes for parallel listing")

    # List in parallel
    total_files = 0
    seen = set()
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {
            pool.submit(self._list_cloudtrail_prefix, s3, bucket, p, globs, logger): p
            for p in prefixes
        }
        for future in as_completed(futures):
            prefix = futures[future]
            try:
                files = future.result()
                for f in files:
                    if f.uri not in seen:
                        seen.add(f.uri)
                        total_files += 1
                        yield f
            except Exception as exc:
                logger.error(f"Error listing prefix {prefix}: {exc}")
                raise

    logger.info(f"CloudTrail listing complete: {total_files} files from {len(prefixes)} prefixes")

def _get_matching_files_default(self, globs, base_prefix, logger):
    """Fallback: original broad listing."""
    s3 = self.s3_client
    seen = set()
    for remote_file in self._page(s3, globs, self.config.bucket, base_prefix, seen, logger):
        yield remote_file
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/v4/test_cloudtrail_listing.py unit_tests/v4/test_cloudtrail_cursor.py -v
```

Expected: All pass

- [ ] **Step 5: Run ALL existing tests to check for regressions**

```bash
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/ -v --tb=short 2>&1 | tail -30
```

Expected: No new failures

- [ ] **Step 6: Commit**

```bash
git add source_s3/v4/stream_reader.py unit_tests/v4/test_cloudtrail_listing.py
git commit -m "feat: add date-aware parallel prefix listing for CloudTrail

Generates per-day S3 prefixes from cursor date to today, lists them
in parallel with 10 threads. Reduces listing from hours to seconds
for buckets with millions of files.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Integration Wiring (source.py + config.py)

**Files:**
- Modify: `source_s3/v4/source.py`
- Modify: `source_s3/v4/config.py`

- [ ] **Step 1: Add `cloudtrail_regions` to config**

In `source_s3/v4/config.py`, add after `flatten_records_key`:

```python
    cloudtrail_regions: Optional[List[str]] = Field(
        title="CloudTrail Regions",
        default=None,
        description="Optional list of AWS regions to sync CloudTrail logs from. If not set, regions are auto-discovered from the S3 bucket.",
        examples=[["us-east-1", "eu-west-1"]],
        order=9,
    )
```

Also add `List` to the imports if not already there.

- [ ] **Step 2: Wire cursor state to reader in source.py**

Modify `source_s3/v4/source.py`:

**Add import:**
```python
from datetime import datetime
```

**Override `streams()` to bridge cursor state:**
```python
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        result = super().streams(config)
        # Bridge cursor state to reader for CloudTrail date-aware listing
        flatten_records_key = getattr(self.main_config, 'flatten_records_key', None)
        if flatten_records_key and self.state:
            self._bridge_cloudtrail_cursor_to_reader()
        return result

    def _bridge_cloudtrail_cursor_to_reader(self) -> None:
        """Extract cloudtrail_cursor from state and set on stream reader."""
        for state_msg in self.state:
            try:
                # state_msg is an AirbyteStateMessage
                stream_state = state_msg.stream.stream_state if state_msg.stream else None
                if stream_state and "cloudtrail_cursor" in stream_state:
                    cursor_str = stream_state["cloudtrail_cursor"]
                    cursor_dt = datetime.strptime(cursor_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    self.stream_reader.set_cloudtrail_cursor_date(cursor_dt)
                    return
            except (AttributeError, KeyError, ValueError):
                continue
```

**Modify `_make_default_stream()` to pass `flatten_records_key` to cursor:**

The cursor is created in `super().streams()` via `self.cursor_cls(stream_config)`. Since we can't easily change that call, we need the cursor to get `flatten_records_key` a different way. The simplest: store it on the class after `_get_parsed_config`:

```python
    def _get_parsed_config(self, config: Mapping[str, Any]) -> AbstractFileBasedSpec:
        self.main_config = self.spec_class(**config)
        return self.main_config
```

And override the cursor creation. Looking at the CDK, path 3 does `cursor = self.cursor_cls(stream_config)`. We can't intercept this directly without overriding `streams()` more deeply. The simplest approach: make `Cursor.__init__` read `flatten_records_key` from a class-level attribute set before `super().streams()`:

In `source.py`, modify `streams()`:
```python
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        parsed = self._get_parsed_config(config)
        # Set flatten_records_key on Cursor class before streams are created
        Cursor._flatten_records_key = getattr(parsed, 'flatten_records_key', None)
        result = super().streams(config)
        # Bridge cursor state to reader
        if Cursor._flatten_records_key and self.state:
            self._bridge_cloudtrail_cursor_to_reader()
        return result
```

And in `cursor.py`, update `__init__`:
```python
    _flatten_records_key: Optional[str] = None  # Set by SourceS3.streams() before construction

    def __init__(self, stream_config: FileBasedStreamConfig, **_: Any):
        super().__init__(stream_config)
        self._running_migration = False
        self._v3_migration_start_datetime = None
        self._cloudtrail_mode = bool(Cursor._flatten_records_key)
        self._cloudtrail_cursor_dt: Optional[datetime] = None
```

- [ ] **Step 3: Run all tests**

```bash
PYTHONPATH=. $(poetry env info --path)/bin/python -m pytest unit_tests/ -v --tb=short 2>&1 | tail -30
```

- [ ] **Step 4: Commit**

```bash
git add source_s3/v4/source.py source_s3/v4/config.py source_s3/v4/cursor.py
git commit -m "feat: wire CloudTrail cursor state to stream reader

Bridge cursor state to reader via streams() override. Add
cloudtrail_regions optional config. Cursor reads flatten_records_key
from class attribute set before construction.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Real-World Test Against Forter Bucket

Test the connector locally against the real Forter CloudTrail bucket to validate the optimization.

- [ ] **Step 1: Create a test script**

Create `scripts/test_forter_listing.py` (not committed):

```python
"""
Test the CloudTrail listing optimization against real Forter data.
Compares old (broad prefix) vs new (date-aware) listing performance.

Usage:
    cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
    PYTHONPATH=. $(poetry env info --path)/bin/python scripts/test_forter_listing.py
"""
import time
import logging
import boto3
from datetime import datetime

from source_s3.v4.stream_reader import SourceS3StreamReader
from source_s3.v4.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

# Create reader with Forter config
reader = SourceS3StreamReader()

# Build config matching Forter's connection
config = Config(
    bucket="forter-log-archive-store-all",
    streams=[],
    role_arn="arn:aws:iam::168921644498:role/FabrixBucketReader_forter-log-archive-store-all",
    external_id="99225dda35cd4c5791c2f16a",
    start_date="2024-11-22T11:58:08.763753Z",
    flatten_records_key="Records",
)
reader.config = config

globs = ["AWSLogs/174522763890/CloudTrail/**/*.json.gz"]

# Test 1: NEW - date-aware listing (cursor from 3 days ago)
reader.set_cloudtrail_cursor_date(datetime(2026, 3, 19, 0, 0, 0))
logger.info("=== NEW: Date-aware listing (last 3 days) ===")
t0 = time.perf_counter()
new_files = list(reader.get_matching_files(globs, None, logger))
new_time = time.perf_counter() - t0
logger.info(f"NEW: {len(new_files)} files in {new_time:.1f}s")

# Test 2: OLD - broad listing (first 60 seconds only)
reader._cloudtrail_cursor_date = None  # disable optimization
reader._config.flatten_records_key = None  # force old path
logger.info("\n=== OLD: Broad prefix listing (60s sample) ===")
t0 = time.perf_counter()
old_count = 0
for f in reader.get_matching_files(globs, None, logger):
    old_count += 1
    if time.perf_counter() - t0 > 60:
        break
old_time = time.perf_counter() - t0
logger.info(f"OLD: {old_count} files in {old_time:.1f}s (stopped at 60s)")

print(f"\n{'='*60}")
print(f"NEW: {len(new_files)} files in {new_time:.1f}s")
print(f"OLD: {old_count} files in {old_time:.1f}s (partial, 60s cap)")
print(f"Estimated OLD total: {old_count / old_time * 282:.0f} files (based on 282s full listing)")
```

- [ ] **Step 2: Run the test** (requires AWS SSO login with production profile — the connector pod uses EKS IAM, but locally we need explicit creds)

Note: This test requires the Forter bucket role to be assumable. If running locally, ensure AWS credentials are configured. In EKS, the pod's service account handles this.

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
PYTHONPATH=. $(poetry env info --path)/bin/python scripts/test_forter_listing.py
```

- [ ] **Step 3: Clean up test script**

```bash
rm scripts/test_forter_listing.py
```

---

### Task 5: Build and Deploy as New Version

Build the connector Docker image, push to ECR, and register as a new custom connector in Airbyte for testing.

- [ ] **Step 1: Update version in pyproject.toml**

Change the version to distinguish from current production:
```
version = "4.14.0"
```
(Current production is 4.13.4)

- [ ] **Step 2: Build Docker images**

```bash
cd /Users/orasaf/git/airbyte/airbyte-integrations/connectors/source-s3
poe build-arm
poe build-amd
```

- [ ] **Step 3: Authenticate to ECR**

```bash
aws ecr get-login-password --region us-east-1 --profile production | docker login --username AWS --password-stdin 794038212761.dkr.ecr.us-east-1.amazonaws.com
```

- [ ] **Step 4: Push to ECR with new version**

```bash
VERSION=4.14.0 poe ecr-push-all
VERSION=4.14.0 poe manifest-push-version
```

- [ ] **Step 5: Register as new custom connector in Airbyte**

In the Airbyte UI (Settings → Sources → Add New Connector):
- Docker Repository: `794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker`
- Docker Image Tag: `4.14.0`
- Connector Display Name: `Source S3 (CloudTrail Optimized)`

- [ ] **Step 6: Create a test connection using Fabrix tenant**

Create a new connection in Airbyte using the new connector, pointed at a CloudTrail S3 bucket accessible by the Fabrix tenant. Configure with `flatten_records_key: Records`. Run a sync and verify:
- Listing completes in seconds (check logs)
- Records arrive in Snowflake
- Cursor state includes `cloudtrail_cursor`

- [ ] **Step 7: Commit version bump**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 4.14.0 for CloudTrail optimization

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```
