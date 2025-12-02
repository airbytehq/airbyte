# Mock Server Tests Playbook for Declarative Connectors

This playbook provides step-by-step guidance for writing mock server tests for Airbyte declarative (manifest-only) connectors. These tests use the airbyte-cdk's HttpMocker to simulate upstream API responses, enabling fast, deterministic testing without real credentials or network calls.

## Purpose and Scope

Mock server tests validate that a connector's manifest configuration (HTTP paths, authentication, pagination, incremental cursors, error handlers) behaves as expected. They are Python unit/integration tests that run entirely offline, making them safe for CI, forks, and local development.

This playbook targets declarative connectors that have a `manifest.yaml` file and use the `HttpRequester`/`SimpleRetriever` stack. You can identify these connectors by checking `metadata.yaml` for tags like `language:manifest-only` and `cdk:low-code`.

## Step 1: Understand the Connector

Before writing tests, thoroughly analyze the connector's configuration.

### 1.1 Locate and Confirm Connector Type

Navigate to the connector directory and verify it's declarative:

```bash
cd airbyte-integrations/connectors/source-<name>/
ls -la
```

Confirm these files exist:
- `manifest.yaml` - The declarative connector definition
- `metadata.yaml` - Connector metadata with tags

Check `metadata.yaml` for declarative indicators:

```yaml
tags:
  - language:manifest-only
  - cdk:low-code
```

### 1.2 Identify All Streams

Extract stream names from the manifest:

```bash
grep "name:" manifest.yaml | grep -v "field_name\|stream_name\|class_name"
```

For each stream, document these key properties from `manifest.yaml`:

| Property | Location in Manifest | Purpose |
|----------|---------------------|---------|
| Path | `requester.path` | API endpoint |
| HTTP Method | `requester.http_method` | GET, POST, etc. |
| Query Parameters | `requester.request_parameters` | per_page, page, etc. |
| Record Extraction | `record_selector.extractor.field_path` | Where records live in response |
| Pagination Type | `paginator.pagination_strategy.type` | CursorPagination, OffsetIncrement, etc. |
| Page Size | `paginator.pagination_strategy.page_size` | Records per page |
| Cursor Field | `incremental_sync.cursor_field` | Field for incremental sync |
| Datetime Format | `incremental_sync.datetime_format` | Format for date parameters |
| Start Time Parameter | `incremental_sync.start_time_option.field_name` | Query param name (e.g., updated_since) |

### 1.3 Select Streams for Testing (Minimum 50% Coverage Required)

You must test at least 50% of all streams in the connector. Count the total number of streams and ensure your test coverage meets this threshold.

When selecting which streams to test, prioritize:

1. Streams listed in `metadata.yaml` under `suggestedStreams.streams`
2. Streams that exercise different patterns:
   - Simple streams without pagination (e.g., `company` endpoint returning single object)
   - Paginated collections using cursor-based pagination (`links.next`)
   - Paginated collections using offset-based pagination (`page`/`per_page`)
   - Incremental streams with `DatetimeBasedCursor`
   - Substreams that depend on parent streams (`SubstreamPartitionRouter`)

The goal is to cover at least 50% of streams while ensuring each distinct pattern is tested at least once.

## Step 2: Create Test Directory Structure

Create the following structure under the connector root:

```
source-<name>/
  manifest.yaml
  metadata.yaml
  unit_tests/
    pyproject.toml
    conftest.py
    integration/
      __init__.py
      config.py
      request_builder.py
      utils.py
      test_<stream1>.py
      test_<stream2>.py
      ...
    resource/
      http/
        response/
          <stream1>.json
          <stream2>.json
          ...
```

### 2.1 pyproject.toml

Create a minimal test project configuration:

```toml
[tool.poetry]
name = "unit_tests"
version = "0.1.0"
description = "Unit tests for source-<name>"
authors = ["Airbyte <contact@airbyte.io>"]

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.group.dev.dependencies]
airbyte-cdk = "^6.0.0"
pytest = "^8.0.0"
freezegun = "^1.2.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 2.2 conftest.py

Create test-wide fixtures and helpers:

```python
import os
from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from pytest import fixture


def _get_manifest_path() -> Path:
    """Get path to manifest.yaml, handling both CI and local environments."""
    # CI path (inside Docker container)
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    # Local development path
    return Path(__file__).parent.parent


def get_source(config: Mapping[str, Any]) -> ManifestDeclarativeSource:
    """Create a ManifestDeclarativeSource instance with the given config."""
    manifest_path = _get_manifest_path() / "manifest.yaml"
    return ManifestDeclarativeSource(
        source_config=config,
        path_to_manifest=manifest_path,
    )


@fixture(autouse=True)
def clear_cache_before_each_test():
    """Clear HTTP request cache between tests to ensure isolation."""
    cache_path = os.getenv("REQUEST_CACHE_PATH")
    if cache_path:
        cache_dir = Path(cache_path)
        if cache_dir.exists():
            for file_path in cache_dir.glob("*.sqlite"):
                file_path.unlink()
    yield
```

### 2.3 integration/config.py

Define test configuration matching the connector's spec:

```python
from typing import Any, Mapping

# Match these to your connector's spec.json / manifest.yaml spec
_ACCOUNT_ID = "test_account_123"
_API_TOKEN = "test_api_token_abc"
_START_DATE = "2024-01-01T00:00:00Z"  # Must match datetime_format in manifest!


class ConfigBuilder:
    """Builder for creating test configurations."""

    def __init__(self) -> None:
        self._account_id = _ACCOUNT_ID
        self._api_token = _API_TOKEN
        self._start_date = _START_DATE

    def with_account_id(self, account_id: str) -> "ConfigBuilder":
        self._account_id = account_id
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def build(self) -> Mapping[str, Any]:
        return {
            "account_id": self._account_id,
            "credentials": {
                "auth_type": "Token",
                "api_token": self._api_token,
            },
            "replication_start_date": self._start_date,
        }
```

### 2.4 integration/request_builder.py

Create helpers for constructing HttpRequest objects:

```python
from typing import Optional
from airbyte_cdk.test.mock_http.request import HttpRequest

_BASE_URL = "https://api.example.com/v2"


class RequestBuilder:
    """Builder for creating HttpRequest objects for testing."""

    @classmethod
    def endpoint(cls, resource: str) -> "RequestBuilder":
        return cls(resource)

    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._per_page: Optional[int] = None
        self._page: Optional[int] = None
        self._updated_since: Optional[str] = None

    def with_per_page(self, per_page: int) -> "RequestBuilder":
        self._per_page = per_page
        return self

    def with_page(self, page: int) -> "RequestBuilder":
        self._page = page
        return self

    def with_updated_since(self, updated_since: str) -> "RequestBuilder":
        self._updated_since = updated_since
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        if self._per_page:
            query_params["per_page"] = str(self._per_page)
        if self._page:
            query_params["page"] = str(self._page)
        if self._updated_since:
            query_params["updated_since"] = self._updated_since

        return HttpRequest(
            url=f"{_BASE_URL}/{self._resource}",
            query_params=query_params if query_params else None,
        )
```

### 2.5 integration/utils.py

Create catalog and read helpers:

```python
import json
from pathlib import Path
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def get_json_response(filename: str) -> str:
    """Load a JSON response template from the resource directory."""
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / filename
    return response_path.read_text()


def read_stream(
    source: ManifestDeclarativeSource,
    config: Mapping[str, Any],
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[Mapping[str, Any]]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """Read records from a single stream."""
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        source=source,
        config=config,
        catalog=catalog,
        state=state,
        expecting_exception=expecting_exception,
    )
```

## Step 3: Design Mock Responses

The response format must match what the connector expects based on `record_selector.extractor.field_path`.

### 3.1 Determine Response Shape from Manifest

Check the `field_path` in the manifest:

```yaml
record_selector:
  type: RecordSelector
  extractor:
    type: DpathExtractor
    field_path:
      - clients  # Records are under "clients" key
```

This means your mock response should be:

```json
{
  "clients": [
    {"id": 1, "name": "Client 1"},
    {"id": 2, "name": "Client 2"}
  ],
  "per_page": 50,
  "total_pages": 1,
  "page": 1,
  "links": {}
}
```

If `field_path: []` (empty), records are at the root level:

```json
[
  {"id": 1, "name": "Item 1"},
  {"id": 2, "name": "Item 2"}
]
```

### 3.2 Include Pagination Metadata

For cursor-based pagination (using `links.next`):

First page (has more pages):
```json
{
  "clients": [...],
  "links": {
    "next": "https://api.example.com/v2/clients?page=2&per_page=50"
  }
}
```

Last page (no more pages):
```json
{
  "clients": [...],
  "links": {}
}
```

For offset-based pagination:
```json
{
  "clients": [...],
  "page": 1,
  "per_page": 50,
  "total_pages": 3,
  "total_entries": 125
}
```

### 3.3 Store Responses as JSON Files

Create response templates in `unit_tests/resource/http/response/`:

```json
// clients.json
{
  "clients": [
    {
      "id": 101,
      "name": "Test Client",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "per_page": 50,
  "total_pages": 1,
  "page": 1,
  "links": {}
}
```

## Step 4: Write Tests

### 4.1 Basic Full Refresh Test

```python
import freezegun
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.mock_http.response import HttpResponse

from unit_tests.conftest import get_source
from unit_tests.integration.config import ConfigBuilder
from unit_tests.integration.request_builder import RequestBuilder
from unit_tests.integration.utils import get_json_response, read_stream

_STREAM_NAME = "clients"


class TestClientsStream(TestCase):

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T00:00:00Z")
    def test_full_refresh_single_page(self, http_mocker: HttpMocker) -> None:
        """Test basic full refresh sync with a single page of results."""
        # Arrange
        config = ConfigBuilder().build()

        http_mocker.get(
            RequestBuilder.endpoint("clients").with_per_page(50).build(),
            HttpResponse(body=get_json_response("clients.json"), status_code=200),
        )

        # Act
        source = get_source(config)
        output = read_stream(source, config, _STREAM_NAME, SyncMode.full_refresh)

        # Assert
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 101
        assert output.records[0].record.data["name"] == "Test Client"
```

### 4.2 Pagination Test

```python
    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T00:00:00Z")
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker) -> None:
        """Test that connector follows pagination links correctly."""
        config = ConfigBuilder().build()

        # First page with next link
        http_mocker.get(
            RequestBuilder.endpoint("clients").with_per_page(50).build(),
            HttpResponse(
                body="""{
                    "clients": [{"id": 1, "name": "Client 1"}],
                    "links": {"next": "https://api.example.com/v2/clients?page=2&per_page=50"}
                }""",
                status_code=200,
            ),
        )

        # Second page (last page)
        http_mocker.get(
            HttpRequest(url="https://api.example.com/v2/clients?page=2&per_page=50"),
            HttpResponse(
                body="""{
                    "clients": [{"id": 2, "name": "Client 2"}],
                    "links": {}
                }""",
                status_code=200,
            ),
        )

        source = get_source(config)
        output = read_stream(source, config, _STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 2
```

### 4.3 Incremental Sync Test

```python
    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T00:00:00Z")
    def test_incremental_sync(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with updated_since parameter."""
        start_date = "2024-01-01T00:00:00Z"
        config = ConfigBuilder().with_start_date(start_date).build()

        # Mock request with updated_since parameter
        http_mocker.get(
            RequestBuilder.endpoint("clients")
                .with_per_page(50)
                .with_updated_since(start_date)
                .build(),
            HttpResponse(body=get_json_response("clients.json"), status_code=200),
        )

        source = get_source(config)
        output = read_stream(source, config, _STREAM_NAME, SyncMode.incremental)

        assert len(output.records) == 1
        # Verify state was emitted (if your test harness exposes it)
```

### 4.4 Error Handling Test

```python
    @HttpMocker()
    def test_handles_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test that connector handles authentication errors gracefully."""
        config = ConfigBuilder().build()

        http_mocker.get(
            RequestBuilder.endpoint("clients").with_per_page(50).build(),
            HttpResponse(
                body='{"error": "invalid_token"}',
                status_code=401,
            ),
        )

        source = get_source(config)
        # If manifest has IGNORE action for 401, expect no records but no exception
        output = read_stream(
            source, config, _STREAM_NAME,
            expecting_exception=False  # Adjust based on manifest error_handler
        )

        assert len(output.records) == 0
```

## Step 5: Run and Debug Tests

### 5.1 Install Dependencies

```bash
cd airbyte-integrations/connectors/source-<name>/unit_tests
poetry install --no-root --all-extras
```

### 5.2 Run Tests

```bash
# Run all tests
poetry run pytest -v

# Run specific test file
poetry run pytest integration/test_clients.py -v

# Run specific test with output
poetry run pytest integration/test_clients.py::TestClientsStream::test_full_refresh -v -s
```

### 5.3 Debug Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| `Failed to parse JSON data... Expecting value: line 1 column 1` | Mock response body is empty or wrong format | Check `field_path` in manifest and match response structure |
| `ValueError: Invalid number of matches for <HttpRequest>` | Request doesn't match mock | Print actual request or use ANY_QUERY_PARAMS temporarily |
| `manifest.yaml not found` | Path issue in CI vs local | Update `_get_manifest_path()` to handle both environments |
| Flaky tests with different results | Time-dependent code | Add `@freezegun.freeze_time()` decorator |
| Zero records in incremental test | Date format mismatch | Ensure `start_date` format matches `datetime_format` in manifest |
| Pagination stops early | Mock doesn't have enough records | For OffsetIncrement, page must be full (page_size records) to fetch next |

## Step 6: Create PR

After tests pass locally:

1. Create PR with descriptive title: `test(source-<name>): Add mock server tests`
2. Wait for CI to complete

## Quick Reference Checklist

- [ ] Confirm connector is declarative (`manifest.yaml` exists, `language:manifest-only` tag)
- [ ] List all streams from manifest and count total
- [ ] Identify patterns: simple, paginated, incremental, substreams
- [ ] Select streams for testing (minimum 50% of total streams required)
- [ ] Create `unit_tests/` directory structure
- [ ] Create `pyproject.toml` with dependencies
- [ ] Create `conftest.py` with `get_source()` and cache clearing
- [ ] Create `config.py` with test configuration matching spec
- [ ] Create `request_builder.py` for HttpRequest construction
- [ ] Create `utils.py` with read helpers
- [ ] Create JSON response templates in `resource/http/response/`
- [ ] Write tests for each selected stream:
  - [ ] Full refresh test
  - [ ] Pagination test (if applicable)
  - [ ] Incremental sync test (if applicable)
  - [ ] Error handling test (if applicable)
- [ ] Run tests locally: `poetry run pytest -v`
- [ ] Fix any failures and iterate
- [ ] Create PR and wait for CI

## Additional Resources

- Reference gist with detailed examples: https://gist.github.com/ChristoGrab/bbf7171c508cc161be3cb4286d5a4daf
- Example connectors with tests: `source-stripe`, `source-zendesk-support`, `source-hubspot`
- airbyte-cdk test utilities: `airbyte_cdk.test.mock_http`
