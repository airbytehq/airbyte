# Mock Server Tests for Connectors

Mock server tests provide a fast, reliable way to test connector behavior without making actual API calls. These tests use the Airbyte Python CDK's mock HTTP framework to simulate API responses and verify connector logic.

## Why Use Mock Server Tests

Mock server tests offer several advantages over integration tests:

- **Speed**: Tests run in milliseconds without network latency
- **Reliability**: No dependency on external API availability or rate limits
- **Isolation**: Test specific scenarios without affecting production data
- **Determinism**: Consistent results without API changes or data variations
- **Cost**: No API usage costs or quota consumption

Mock server tests complement integration tests by providing fast feedback during development while integration tests verify real API behavior.

## Testing Framework Overview

The mock server testing framework is available in the [airbyte-python-cdk](https://github.com/airbytehq/airbyte-python-cdk/tree/main/airbyte_cdk/test) and provides the following components:

### Core Components

**HttpMocker**: Context manager and decorator that intercepts HTTP requests and returns mocked responses.

```python
from airbyte_cdk.test.mock_http import HttpMocker

@HttpMocker()
def test_example(http_mocker: HttpMocker):
    # Configure mock responses
    http_mocker.get(request, response)
    # Run connector code
```

**HttpRequest**: Represents an HTTP request with URL, query parameters, headers, and body.

```python
from airbyte_cdk.test.mock_http import HttpRequest

request = HttpRequest(
    url="https://api.example.com/v1/users",
    query_params={"limit": "100"},
    headers={"Authorization": "Bearer token"},
)
```

**HttpResponse**: Represents an HTTP response with body, status code, and headers.

```python
from airbyte_cdk.test.mock_http import HttpResponse

response = HttpResponse(
    body='{"data": [{"id": "123"}]}',
    status_code=200,
)
```

**Response Builders**: Helper classes to construct responses from templates with dynamic data.

```python
from airbyte_cdk.test.mock_http.response_builder import (
    create_response_builder,
    create_record_builder,
    find_template,
    FieldPath,
    NestedPath,
)

# Load response template from JSON file
response_template = find_template("users", __file__)

# Create response builder
response_builder = create_response_builder(
    response_template=response_template,
    records_path=FieldPath("data"),
    pagination_strategy=MyPaginationStrategy(),
)

# Create record builder
record_builder = create_record_builder(
    response_template=response_template,
    records_path=FieldPath("data"),
    record_id_path=FieldPath("id"),
    record_cursor_path=FieldPath("updated_at"),
)
```

### Test Utilities

**EntrypointWrapper**: Executes connector operations (read, check, discover) and captures output.

```python
from airbyte_cdk.test.entrypoint_wrapper import read

output = read(source, config, catalog, state)
assert len(output.records) == 10
```

**CatalogBuilder**: Constructs configured catalogs for testing.

```python
from airbyte_cdk.test.catalog_builder import CatalogBuilder

catalog = CatalogBuilder().with_stream("users", SyncMode.incremental).build()
```

**StateBuilder**: Constructs state messages for incremental sync testing.

```python
from airbyte_cdk.test.state_builder import StateBuilder

state = StateBuilder().with_stream_state("users", {"updated_at": "2023-01-01"}).build()
```

## Test Organization

Organize mock server tests in a dedicated directory structure:

```
airbyte-integrations/connectors/source-example/
├── unit_tests/
│   ├── integration/                    # Mock server tests
│   │   ├── __init__.py
│   │   ├── config.py                   # ConfigBuilder for test configs
│   │   ├── request_builder.py          # RequestBuilder for API requests
│   │   ├── response_builder.py         # Response helpers
│   │   ├── pagination.py               # Pagination strategies
│   │   ├── test_users.py               # Tests for users stream
│   │   ├── test_orders.py              # Tests for orders stream
│   │   └── utils.py                    # Shared test utilities
│   ├── resource/
│   │   └── http/
│   │       └── response/               # JSON response templates
│   │           ├── users.json
│   │           ├── orders.json
│   │           ├── 400.json            # Error responses
│   │           ├── 401.json
│   │           ├── 429.json
│   │           └── 500.json
│   └── conftest.py                     # Pytest fixtures
```

## Best Practices

### 1. Keep Tests Minimal

Tests should only configure values that are necessary for the specific scenario being tested. Avoid setting unnecessary fields or using complete API responses when a minimal response suffices.

**Good Example** (minimal):
```python
@HttpMocker()
def test_pagination(http_mocker: HttpMocker):
    # First page - only set pagination token
    http_mocker.get(
        _request().with_limit(100).build(),
        _response()
            .with_pagination()  # Sets next_token
            .with_record(_record().with_id("last_id"))
            .build(),
    )
    
    # Second page - only set starting_after
    http_mocker.get(
        _request().with_starting_after("last_id").with_limit(100).build(),
        _response().with_record(_record()).build(),
    )
    
    output = _read(config())
    assert len(output.records) == 2
```

**Bad Example** (excessive configuration):
```python
@HttpMocker()
def test_pagination(http_mocker: HttpMocker):
    # Unnecessarily configures all fields
    http_mocker.get(
        _request()
            .with_limit(100)
            .with_created_gte(start_date)
            .with_created_lte(end_date)
            .with_types(["charge.succeeded"])
            .with_expands(["customer", "invoice"])
            .build(),
        _response()
            .with_pagination()
            .with_record(_record()
                .with_id("last_id")
                .with_cursor(1234567890)
                .with_field(FieldPath("amount"), 1000)
                .with_field(FieldPath("currency"), "usd")
                .with_field(FieldPath("status"), "succeeded"))
            .build(),
    )
    # ... rest of test
```

### 2. Make Tests Expressive

Tests should explicitly show values that affect the test outcome. If a test depends on a specific field value, set it in the test context rather than relying on values in template files.

**Good Example** (expressive):
```python
@HttpMocker()
def test_incremental_sync_uses_cursor(http_mocker: HttpMocker):
    cursor_value = 1234567890
    
    http_mocker.get(
        _request().with_created_gte(cursor_value).build(),
        _response().with_record(_record().with_cursor(cursor_value + 100)).build(),
    )
    
    output = _read(
        config(),
        state=StateBuilder().with_stream_state("events", {"created": cursor_value}).build(),
    )
    
    # Test explicitly shows cursor value affects query params and state
    assert output.most_recent_state.stream_state.created == str(cursor_value + 100)
```

**Bad Example** (implicit dependencies):
```python
@HttpMocker()
def test_incremental_sync_uses_cursor(http_mocker: HttpMocker):
    # Cursor value hidden in template file
    http_mocker.get(
        _request().build(),
        _response().with_record(_record()).build(),
    )
    
    # State value not shown in test
    output = _read(config(), state=_some_state())
    
    # Unclear what cursor value is being tested
    assert output.most_recent_state is not None
```

### 3. Ensure Tests Are Fast

Mock server tests should execute quickly. Disable any sleep or delay mechanisms using monkey patching.

**Good Example** (fast):
```python
@HttpMocker()
def test_retry_on_rate_limit(http_mocker: HttpMocker, mocker):
    # Disable sleep to make test fast
    mocker.patch("time.sleep", lambda x: None)
    
    http_mocker.get(
        _request().build(),
        [
            _response_with_status(429),  # Rate limited
            _response().with_record(_record()).build(),  # Success
        ],
    )
    
    output = _read(config())
    assert len(output.records) == 1
```

**Bad Example** (slow):
```python
@HttpMocker()
def test_retry_on_rate_limit(http_mocker: HttpMocker):
    # Test will sleep during retries, making it slow
    http_mocker.get(
        _request().build(),
        [
            _response_with_status(429),
            _response().with_record(_record()).build(),
        ],
    )
    
    output = _read(config())
    assert len(output.records) == 1
```

### 4. Avoid Fragile Tests

Tests should not fail when the API provider adds new fields to responses. Only validate fields that are important for the connector's functionality (filtering, transformation, cursor tracking, etc.).

**Good Example** (not fragile):
```python
@HttpMocker()
def test_filters_by_status(http_mocker: HttpMocker):
    # Only set the field that matters for filtering
    http_mocker.get(
        _request().with_status("active").build(),
        _response()
            .with_record(_record().with_field(FieldPath("status"), "active"))
            .build(),
    )
    
    output = _read(config().with_status_filter("active"))
    # Only assert on the filtered field
    assert all(record.record.data["status"] == "active" for record in output.records)
```

**Bad Example** (fragile):
```python
@HttpMocker()
def test_filters_by_status(http_mocker: HttpMocker):
    # Sets all fields explicitly
    http_mocker.get(
        _request().with_status("active").build(),
        _response()
            .with_record(_record()
                .with_field(FieldPath("id"), "123")
                .with_field(FieldPath("name"), "Test")
                .with_field(FieldPath("status"), "active")
                .with_field(FieldPath("created_at"), 1234567890)
                .with_field(FieldPath("updated_at"), 1234567890)
                .with_field(FieldPath("email"), "test@example.com")
                # ... many more fields
            )
            .build(),
    )
    
    output = _read(config().with_status_filter("active"))
    # Asserts on all fields - will break if API adds new fields
    assert output.records[0].record.data == {
        "id": "123",
        "name": "Test",
        "status": "active",
        # ... all fields must match exactly
    }
```

### 5. Use Builder Pattern

Use builder classes to construct requests, responses, and configurations. This makes tests more readable and maintainable.

**Request Builder Example**:
```python
class RequestBuilder:
    @classmethod
    def users_endpoint(cls, account_id: str, api_key: str) -> "RequestBuilder":
        return cls("users", account_id, api_key)
    
    def __init__(self, resource: str, account_id: str, api_key: str):
        self._resource = resource
        self._account_id = account_id
        self._api_key = api_key
        self._query_params = {}
    
    def with_limit(self, limit: int) -> "RequestBuilder":
        self._query_params["limit"] = str(limit)
        return self
    
    def with_created_gte(self, created_gte: datetime) -> "RequestBuilder":
        self._query_params["created[gte]"] = str(int(created_gte.timestamp()))
        return self
    
    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.example.com/v1/{self._resource}",
            query_params=self._query_params,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
```

**Config Builder Example**:
```python
class ConfigBuilder:
    def __init__(self):
        self._config = {
            "api_key": "test_api_key",
            "account_id": "test_account",
            "start_date": "2023-01-01T00:00:00Z",
        }
    
    def with_start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self
    
    def with_account_id(self, account_id: str) -> "ConfigBuilder":
        self._config["account_id"] = account_id
        return self
    
    def build(self) -> Dict[str, str]:
        return self._config
```

### 6. Use Response Templates

Store API response templates in JSON files and use the response builder to construct responses with dynamic data.

**Response Template** (`unit_tests/resource/http/response/users.json`):
```json
{
  "object": "list",
  "data": [
    {
      "id": "user_123",
      "email": "user@example.com",
      "created": 1234567890,
      "updated": 1234567890
    }
  ],
  "has_more": false
}
```

**Using the Template**:
```python
def _response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template("users", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=MyPaginationStrategy(),
    )

def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template("users", __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("updated"),
    )

@HttpMocker()
def test_example(http_mocker: HttpMocker):
    http_mocker.get(
        _request().build(),
        _response()
            .with_record(_record().with_id("user_456").with_cursor(1234567999))
            .build(),
    )
```

### 7. Test Common Scenarios

Ensure your test suite covers these common scenarios:

**Full Refresh Tests**:
- Single page response
- Multiple pages (pagination)
- Multiple slices (date ranges, partitions)
- Empty response
- Error handling (4xx, 5xx)
- Retry logic

**Incremental Sync Tests**:
- Initial sync with no state
- Subsequent sync with state
- State message generation
- Cursor field handling
- Lookback window behavior

**Error Handling Tests**:
- Rate limiting (429) with retry
- Authentication errors (401)
- Server errors (500) with retry
- Client errors (400) with appropriate failure type

**Example Test Suite Structure**:
```python
@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh:
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker):
        # Test implementation
    
    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(self, http_mocker: HttpMocker):
        # Test implementation
    
    @HttpMocker()
    def test_given_http_status_500_then_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker):
        # Test implementation

@freezegun.freeze_time(NOW.isoformat())
class TestIncremental:
    @HttpMocker()
    def test_given_no_state_when_read_then_return_state(self, http_mocker: HttpMocker):
        # Test implementation
    
    @HttpMocker()
    def test_given_state_when_read_then_use_state_for_query_params(self, http_mocker: HttpMocker):
        # Test implementation
```

## Complete Example

Here's a complete example demonstrating best practices:

**config.py**:
```python
from datetime import datetime
from typing import Dict

class ConfigBuilder:
    def __init__(self):
        self._config = {
            "api_key": "test_api_key",
            "account_id": "test_account",
            "start_date": "2023-01-01T00:00:00Z",
        }
    
    def with_start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self
    
    def build(self) -> Dict[str, str]:
        return self._config
```

**request_builder.py**:
```python
from datetime import datetime
from airbyte_cdk.test.mock_http import HttpRequest

class RequestBuilder:
    @classmethod
    def events_endpoint(cls, account_id: str, api_key: str) -> "RequestBuilder":
        return cls("events", account_id, api_key)
    
    def __init__(self, resource: str, account_id: str, api_key: str):
        self._resource = resource
        self._query_params = {}
        self._api_key = api_key
    
    def with_created_gte(self, created_gte: datetime) -> "RequestBuilder":
        self._query_params["created[gte]"] = str(int(created_gte.timestamp()))
        return self
    
    def with_limit(self, limit: int) -> "RequestBuilder":
        self._query_params["limit"] = str(limit)
        return self
    
    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.example.com/v1/{self._resource}",
            query_params=self._query_params,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
```

**test_events.py**:
```python
from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import RequestBuilder

_STREAM_NAME = "events"
_NOW = datetime.now(timezone.utc)
_START_DATE = _NOW - timedelta(days=30)
_ACCOUNT_ID = "test_account"
_API_KEY = "test_api_key"

def _request() -> RequestBuilder:
    return RequestBuilder.events_endpoint(_ACCOUNT_ID, _API_KEY)

def _config() -> ConfigBuilder:
    return ConfigBuilder().with_start_date(_START_DATE)

def _catalog(sync_mode: SyncMode):
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()

def _record():
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )

def _response():
    return create_response_builder(
        find_template("events", __file__),
        FieldPath("data"),
    )

@freezegun.freeze_time(_NOW.isoformat())
class TestFullRefresh(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker):
        http_mocker.get(
            _request().with_created_gte(_START_DATE).with_limit(100).build(),
            _response().with_record(_record()).with_record(_record()).build(),
        )
        
        output = read(source, _config().build(), _catalog(SyncMode.full_refresh))
        assert len(output.records) == 2
    
    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry(self, http_mocker: HttpMocker, mocker):
        mocker.patch("time.sleep", lambda x: None)
        
        http_mocker.get(
            _request().with_created_gte(_START_DATE).with_limit(100).build(),
            [
                HttpResponse('{"error": "rate_limited"}', 429),
                _response().with_record(_record()).build(),
            ],
        )
        
        output = read(source, _config().build(), _catalog(SyncMode.full_refresh))
        assert len(output.records) == 1

@freezegun.freeze_time(_NOW.isoformat())
class TestIncremental(TestCase):
    @HttpMocker()
    def test_given_state_when_read_then_use_state(self, http_mocker: HttpMocker):
        state_value = _START_DATE + timedelta(days=1)
        cursor_value = int(state_value.timestamp())
        
        http_mocker.get(
            _request().with_created_gte(state_value).with_limit(100).build(),
            _response().with_record(_record().with_cursor(cursor_value + 100)).build(),
        )
        
        state = StateBuilder().with_stream_state("events", {"created": cursor_value}).build()
        output = read(source, _config().build(), _catalog(SyncMode.incremental), state)
        
        assert output.most_recent_state.stream_state.created == str(cursor_value + 100)
```

## Reference Examples

For comprehensive examples of mock server tests, review these connectors:

- [source-stripe](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-stripe/unit_tests/integration) - Extensive test coverage with multiple streams, pagination, and error handling
- [source-amazon-seller-partner](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-amazon-seller-partner/unit_tests/integration) - Report-based streams with complex state management

## Related Topics

- [Python CDK Testing Framework](https://github.com/airbytehq/airbyte-python-cdk/tree/main/airbyte_cdk/test) - Technical reference for testing utilities
- [Connector Development](https://docs.airbyte.com/connector-development/) - General connector development guide
- [Testing Connectors](https://docs.airbyte.com/connector-development/testing-connectors/) - Overview of connector testing approaches
