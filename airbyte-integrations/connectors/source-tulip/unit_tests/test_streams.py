"""Unit tests for TulipTableStream."""

import json
import pytest
from unittest.mock import MagicMock

from source_tulip.streams import TulipTableStream, DEFAULT_LIMIT
from source_tulip.utils import generate_column_name

from unit_tests.conftest import MOCK_CONFIG, MOCK_TABLE_METADATA


def _make_stream(config=None, table_metadata=None):
    """Helper to create a TulipTableStream for testing."""
    cfg = config or MOCK_CONFIG.copy()
    meta = table_metadata or MOCK_TABLE_METADATA.copy()
    return TulipTableStream(
        table_id=meta["id"],
        table_label=meta["label"],
        table_metadata=meta,
        config=cfg,
    )


def _mock_response(data):
    """Create a mock requests.Response with the given JSON data."""
    resp = MagicMock()
    resp.json.return_value = data
    return resp


class TestStreamProperties:
    def test_name(self):
        stream = _make_stream()
        expected = generate_column_name("T123", "Test Table")
        assert stream.name == expected

    def test_url_base(self):
        stream = _make_stream()
        assert stream.url_base == "https://test.tulip.co/api/v3/"

    def test_path_with_workspace(self):
        stream = _make_stream()
        assert stream.path() == "w/W456/tables/T123/records"

    def test_path_without_workspace(self):
        config = MOCK_CONFIG.copy()
        del config["workspace_id"]
        stream = _make_stream(config=config)
        assert stream.path() == "tables/T123/records"

    def test_primary_key(self):
        stream = _make_stream()
        assert stream.primary_key == "id"

    def test_cursor_field(self):
        stream = _make_stream()
        assert stream.cursor_field == "_sequenceNumber"

    def test_checkpoint_interval(self):
        stream = _make_stream()
        assert stream.state_checkpoint_interval == 500

    def test_http_method(self):
        stream = _make_stream()
        assert stream.http_method == "GET"


class TestGetJsonSchema:
    def test_includes_system_fields(self):
        stream = _make_stream()
        schema = stream.get_json_schema()
        props = schema["properties"]
        assert "id" in props
        assert "_createdAt" in props
        assert "_updatedAt" in props
        assert "_sequenceNumber" in props

    def test_includes_custom_fields(self):
        stream = _make_stream()
        schema = stream.get_json_schema()
        props = schema["properties"]
        col1 = generate_column_name("field1", "Field One")
        col2 = generate_column_name("field2", "Field Two")
        assert col1 in props
        assert col2 in props

    def test_excludes_tablelink(self):
        stream = _make_stream()
        schema = stream.get_json_schema()
        props = schema["properties"]
        link_col = generate_column_name("link1", "Link Field")
        assert link_col not in props

    def test_type_mapping_applied(self):
        stream = _make_stream()
        schema = stream.get_json_schema()
        props = schema["properties"]
        int_col = generate_column_name("field2", "Field Two")
        assert props[int_col]["type"] == ["null", "integer"]

    def test_schema_structure(self):
        stream = _make_stream()
        schema = stream.get_json_schema()
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert "properties" in schema


class TestState:
    def test_getter_default(self):
        stream = _make_stream()
        state = stream.state
        assert state["cursor_mode"] == "BOOTSTRAP"
        assert state["last_sequence"] == 0
        assert state["last_updated_at"] is None

    def test_setter_fresh_start(self):
        stream = _make_stream()
        stream.state = {}
        assert stream._cursor_mode == "BOOTSTRAP"
        assert stream._cursor_value == 0
        assert stream._last_updated_at == "2026-01-01T00:00:00Z"  # sync_from_date

    def test_setter_existing_state(self):
        stream = _make_stream()
        stream.state = {
            "cursor_mode": "INCREMENTAL",
            "last_sequence": 500,
            "last_updated_at": "2026-02-01T00:00:00Z",
        }
        assert stream._cursor_mode == "INCREMENTAL"
        assert stream._cursor_value == 500
        assert stream._last_updated_at == "2026-02-01T00:00:00Z"

    def test_setter_migration_from_old_format(self):
        stream = _make_stream()
        stream.state = {"last_updated_at": "2026-01-15T00:00:00Z"}
        assert stream._cursor_mode == "INCREMENTAL"
        assert stream._cursor_value == 0
        assert stream._last_updated_at == "2026-01-15T00:00:00Z"

    def test_setter_handles_none_last_sequence(self):
        stream = _make_stream()
        stream.state = {
            "cursor_mode": "BOOTSTRAP",
            "last_sequence": None,
            "last_updated_at": None,
        }
        assert stream._cursor_value == 0


class TestRequestParams:
    def test_bootstrap_mode(self):
        stream = _make_stream()
        params = stream.request_params()
        assert params["limit"] == DEFAULT_LIMIT
        assert params["offset"] == 0
        filters = json.loads(params["filters"])
        assert any(f["field"] == "_sequenceNumber" for f in filters)

    def test_bootstrap_with_sync_from_date(self):
        stream = _make_stream()
        params = stream.request_params()
        filters = json.loads(params["filters"])
        has_updated_at = any(f["field"] == "_updatedAt" for f in filters)
        assert has_updated_at  # sync_from_date is set in MOCK_CONFIG

    def test_incremental_mode_no_sequence_filter(self):
        """INCREMENTAL should NOT filter on _sequenceNumber (updated records keep old seq)."""
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        stream._last_updated_at = "2026-02-01T00:00:00Z"
        stream._cursor_value = 100
        params = stream.request_params()
        filters = json.loads(params["filters"])
        seq_filters = [f for f in filters if f["field"] == "_sequenceNumber"]
        assert len(seq_filters) == 0  # No _sequenceNumber filter without pagination

    def test_incremental_has_lookback(self):
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        stream._last_updated_at = "2026-02-01T00:01:00Z"
        params = stream.request_params()
        filters = json.loads(params["filters"])
        updated_filter = next(f for f in filters if f["field"] == "_updatedAt")
        # Should have 60s subtracted
        assert updated_filter["arg"] == "2026-02-01T00:00:00Z"

    def test_incremental_with_next_page_token(self):
        """In INCREMENTAL, _sequenceNumber is added only for pagination (next page)."""
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        stream._last_updated_at = "2026-02-01T00:00:00Z"
        params = stream.request_params(next_page_token={"last_sequence": 250})
        filters = json.loads(params["filters"])
        seq_filter = next(f for f in filters if f["field"] == "_sequenceNumber")
        assert seq_filter["arg"] == 250
        # Should also have _updatedAt filter
        assert any(f["field"] == "_updatedAt" for f in filters)

    def test_bootstrap_with_next_page_token(self):
        stream = _make_stream()
        params = stream.request_params(next_page_token={"last_sequence": 250})
        filters = json.loads(params["filters"])
        seq_filter = next(f for f in filters if f["field"] == "_sequenceNumber")
        assert seq_filter["arg"] == 250

    def test_with_custom_filters(self):
        config = MOCK_CONFIG.copy()
        config["custom_filter_json"] = json.dumps(
            [{"field": "status", "functionType": "equal", "arg": "active"}]
        )
        stream = _make_stream(config=config)
        params = stream.request_params()
        filters = json.loads(params["filters"])
        assert any(f.get("field") == "status" for f in filters)

    def test_sort_options(self):
        stream = _make_stream()
        params = stream.request_params()
        sort = json.loads(params["sortOptions"])
        assert sort == [{"sortBy": "_sequenceNumber", "sortDir": "asc"}]

    def test_fields_excludes_tablelink(self):
        stream = _make_stream()
        params = stream.request_params()
        fields = json.loads(params["fields"])
        assert "link1" not in fields
        assert "field1" in fields
        assert "field2" in fields


class TestNextPageToken:
    def test_more_pages(self):
        records = [{"_sequenceNumber": i} for i in range(DEFAULT_LIMIT)]
        resp = _mock_response(records)
        stream = _make_stream()
        token = stream.next_page_token(resp)
        assert token == {"last_sequence": DEFAULT_LIMIT - 1}

    def test_last_page(self):
        records = [{"_sequenceNumber": i} for i in range(50)]
        resp = _mock_response(records)
        stream = _make_stream()
        token = stream.next_page_token(resp)
        assert token is None

    def test_empty_response(self):
        resp = _mock_response([])
        stream = _make_stream()
        token = stream.next_page_token(resp)
        assert token is None


class TestParseResponse:
    def test_transforms_fields(self):
        records = [
            {
                "id": "rec1",
                "field1": "hello",
                "field2": 42,
                "_sequenceNumber": 10,
                "_updatedAt": "2026-01-01T00:00:00Z",
                "_createdAt": "2026-01-01T00:00:00Z",
            }
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        results = list(stream.parse_response(resp))
        assert len(results) == 1
        result = results[0]
        # Custom fields should be mapped
        col1 = generate_column_name("field1", "Field One")
        assert col1 in result
        assert result[col1] == "hello"
        # System fields pass through
        assert result["id"] == "rec1"
        assert result["_sequenceNumber"] == 10

    def test_tracks_cursor_values(self):
        records = [
            {"id": "1", "_sequenceNumber": 5, "_updatedAt": "2026-01-01T00:00:00Z"},
            {"id": "2", "_sequenceNumber": 10, "_updatedAt": "2026-01-02T00:00:00Z"},
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        list(stream.parse_response(resp))
        assert stream._cursor_value == 10
        assert stream._last_updated_at == "2026-01-02T00:00:00Z"

    def test_bootstrap_to_incremental_transition(self):
        # Batch smaller than DEFAULT_LIMIT triggers transition
        records = [
            {"id": "1", "_sequenceNumber": 5, "_updatedAt": "2026-01-01T00:00:00Z"}
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        assert stream._cursor_mode == "BOOTSTRAP"
        list(stream.parse_response(resp))
        assert stream._cursor_mode == "INCREMENTAL"

    def test_no_transition_on_full_batch(self):
        records = [
            {"id": str(i), "_sequenceNumber": i, "_updatedAt": "2026-01-01T00:00:00Z"}
            for i in range(DEFAULT_LIMIT)
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        list(stream.parse_response(resp))
        assert stream._cursor_mode == "BOOTSTRAP"

    def test_empty_response(self):
        resp = _mock_response([])
        stream = _make_stream()
        results = list(stream.parse_response(resp))
        assert results == []

    def test_empty_response_triggers_bootstrap_transition(self):
        """Empty response in BOOTSTRAP mode should transition to INCREMENTAL."""
        resp = _mock_response([])
        stream = _make_stream()
        assert stream._cursor_mode == "BOOTSTRAP"
        list(stream.parse_response(resp))
        assert stream._cursor_mode == "INCREMENTAL"

    def test_empty_response_no_transition_in_incremental(self):
        """Empty response in INCREMENTAL mode should stay INCREMENTAL."""
        resp = _mock_response([])
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        list(stream.parse_response(resp))
        assert stream._cursor_mode == "INCREMENTAL"

    def test_cursor_frozen_during_full_batch(self):
        """_last_updated_at should NOT advance during a full batch (mid-sync)."""
        records = [
            {
                "id": str(i),
                "_sequenceNumber": i,
                "_updatedAt": f"2026-01-{(i % 28) + 1:02d}T00:00:00Z",
            }
            for i in range(DEFAULT_LIMIT)
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        stream._last_updated_at = "2025-12-01T00:00:00Z"
        list(stream.parse_response(resp))
        # Full batch = mid-sync, cursor should stay frozen
        assert stream._last_updated_at == "2025-12-01T00:00:00Z"
        # But max seen should be tracked internally
        assert stream._max_seen_updated_at is not None
        assert stream._max_seen_updated_at > "2025-12-01T00:00:00Z"

    def test_cursor_committed_on_last_batch(self):
        """_last_updated_at should advance only when sync completes (partial batch)."""
        records = [
            {"id": "1", "_sequenceNumber": 1, "_updatedAt": "2026-03-01T00:00:00Z"},
            {"id": "2", "_sequenceNumber": 2, "_updatedAt": "2026-03-15T00:00:00Z"},
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        stream._last_updated_at = "2025-12-01T00:00:00Z"
        list(stream.parse_response(resp))
        # Partial batch = last batch, cursor should be committed
        assert stream._last_updated_at == "2026-03-15T00:00:00Z"
        assert stream._max_seen_updated_at is None  # reset after commit

    def test_state_returns_frozen_value_mid_sync(self):
        """State getter should return the frozen start-of-sync value during mid-sync."""
        records = [
            {"id": str(i), "_sequenceNumber": i, "_updatedAt": "2026-06-01T00:00:00Z"}
            for i in range(DEFAULT_LIMIT)
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        stream._last_updated_at = "2026-01-01T00:00:00Z"
        list(stream.parse_response(resp))
        # Mid-sync: state should return the frozen value
        state = stream.state
        assert state["last_updated_at"] == "2026-01-01T00:00:00Z"

    def test_incremental_filter_uses_frozen_value(self):
        """Incremental filters should use frozen _last_updated_at, not advancing value."""
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        stream._last_updated_at = "2026-01-01T00:00:00Z"

        # Simulate processing a full batch that advances _max_seen_updated_at
        records = [
            {"id": str(i), "_sequenceNumber": i, "_updatedAt": "2026-06-01T00:00:00Z"}
            for i in range(DEFAULT_LIMIT)
        ]
        resp = _mock_response(records)
        list(stream.parse_response(resp))

        # Now request params for the next page - filter should use frozen value
        params = stream.request_params(next_page_token={"last_sequence": 99})
        filters = json.loads(params["filters"])
        updated_filter = next(f for f in filters if f["field"] == "_updatedAt")
        # Should be based on 2026-01-01 minus 60s overlap, NOT 2026-06-01
        assert (
            "2025-12-31" in updated_filter["arg"]
            or "2026-01-01" in updated_filter["arg"]
        )

    def test_incremental_cursor_committed_on_last_batch(self):
        """In INCREMENTAL mode, cursor should commit when last batch is processed."""
        records = [
            {"id": "1", "_sequenceNumber": 1, "_updatedAt": "2026-04-01T00:00:00Z"},
        ]
        resp = _mock_response(records)
        stream = _make_stream()
        stream._cursor_mode = "INCREMENTAL"
        stream._last_updated_at = "2026-01-01T00:00:00Z"
        list(stream.parse_response(resp))
        # Partial batch in INCREMENTAL = last batch, should commit
        assert stream._last_updated_at == "2026-04-01T00:00:00Z"
