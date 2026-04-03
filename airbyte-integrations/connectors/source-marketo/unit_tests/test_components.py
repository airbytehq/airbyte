#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from components import (
    MarketoActivitySchemaLoader,
    MarketoBulkExportCreationRequester,
    MarketoCsvDecoder,
    MarketoLeadsSchemaLoader,
    MarketoRecordTransformation,
    _map_marketo_type,
    clean_string,
    format_value,
)

from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils import AirbyteTracedException


class TestCleanString:
    def test_camel_case(self):
        assert clean_string("updatedAt") == "updated_at"

    def test_pascal_case(self):
        assert clean_string("UpdatedAt") == "updated_at"

    def test_with_spaces(self):
        assert clean_string("base URL") == "base_url"

    def test_already_snake_case(self):
        assert clean_string("updated_at") == "updated_at"

    def test_fix_mapping(self):
        assert clean_string("api method name") == "api_method_name"
        assert clean_string("modifying user") == "modifying_user"


class TestFormatValue:
    def test_null_values(self):
        assert format_value(None, {"type": ["string", "null"]}) is None
        assert format_value("", {"type": ["string", "null"]}) is None
        assert format_value("null", {"type": ["string", "null"]}) is None

    def test_integer(self):
        assert format_value("42", {"type": ["integer", "null"]}) == 42

    def test_integer_with_decimal(self):
        assert format_value("42.7", {"type": ["integer", "null"]}) == 42

    def test_integer_invalid(self):
        assert format_value("abc", {"type": ["integer", "null"]}) is None

    def test_string(self):
        assert format_value("hello", {"type": ["string", "null"]}) == "hello"

    def test_number(self):
        assert format_value("3.14", {"type": ["number", "null"]}) == 3.14

    def test_boolean(self):
        assert format_value("true", {"type": ["boolean", "null"]}) is True
        assert format_value("false", {"type": ["boolean", "null"]}) is False
        assert format_value(True, {"type": ["boolean", "null"]}) is True


class TestMapMarketoType:
    def test_date(self):
        assert _map_marketo_type("date") == {"type": ["string", "null"], "format": "date"}

    def test_datetime(self):
        assert _map_marketo_type("datetime") == {"type": ["string", "null"], "format": "date-time"}

    def test_integer(self):
        assert _map_marketo_type("integer") == {"type": ["integer", "null"]}

    def test_boolean(self):
        assert _map_marketo_type("boolean") == {"type": ["boolean", "null"]}

    def test_string_types(self):
        for st in ["string", "email", "url", "phone", "textarea", "text"]:
            assert _map_marketo_type(st) == {"type": ["string", "null"]}

    def test_array(self):
        result = _map_marketo_type("array")
        assert result["type"] == ["array", "null"]

    def test_unknown(self):
        assert _map_marketo_type("xyz") == {"type": ["string", "null"]}


def _make_streaming_response(text: str) -> Mock:
    """Create a mock response that supports iter_lines (streaming)."""
    response = Mock()
    response.encoding = None
    # Simulate delimiter="\n" by splitting on \n only (not other line separators)
    response.iter_lines = Mock(return_value=iter(text.split("\n")))
    return response


class TestMarketoCsvDecoder:
    def setup_method(self):
        self.decoder = MarketoCsvDecoder(config={}, parameters={})

    def test_decode_basic_csv(self):
        response = _make_streaming_response("Name,Email\nJohn,john@test.com\nJane,jane@test.com")
        records = list(self.decoder.decode(response))
        assert records == [
            {"Name": "John", "Email": "john@test.com"},
            {"Name": "Jane", "Email": "jane@test.com"},
        ]

    def test_decode_filters_null_bytes(self):
        response = _make_streaming_response("Name,Email\nJo\x00hn,john@test.com")
        records = list(self.decoder.decode(response))
        assert records == [{"Name": "John", "Email": "john@test.com"}]

    def test_is_stream_response(self):
        assert self.decoder.is_stream_response() is True

    def test_decode_empty_response(self):
        response = _make_streaming_response("")
        records = list(self.decoder.decode(response))
        assert records == []

    def test_decode_header_only(self):
        response = _make_streaming_response("Name,Email")
        records = list(self.decoder.decode(response))
        assert records == []

    def test_decode_null_values_normalised(self):
        response = _make_streaming_response("Name,Email\nnull,")
        records = list(self.decoder.decode(response))
        assert records == [{"Name": None, "Email": None}]

    def test_decode_column_count_mismatch_raises(self):
        # Simulates a CJK encoding issue where a row has more/fewer columns
        response = _make_streaming_response("Name,Email\nJohn,john@test.com,extra_field")
        with pytest.raises(AirbyteTracedException) as exc_info:
            list(self.decoder.decode(response))
        assert "columns" in exc_info.value.message.lower()

    def test_decode_cjk_characters(self):
        # Ensure CJK characters are handled correctly when column counts match
        response = _make_streaming_response("Name,Email\n\u5f20\u4e09,zhang@test.com")
        records = list(self.decoder.decode(response))
        assert records == [{"Name": "\u5f20\u4e09", "Email": "zhang@test.com"}]

    def test_decode_uses_streaming_with_newline_delimiter(self):
        """Verify decode calls iter_lines with delimiter='\n' to prevent CJK line separator issues."""
        response = _make_streaming_response("Name\nJohn")
        list(self.decoder.decode(response))
        response.iter_lines.assert_called_once_with(decode_unicode=True, delimiter="\n")

    def test_decode_handles_crlf_line_endings(self):
        """Verify \r\n line endings are handled when using \n as delimiter."""
        response = Mock()
        response.encoding = None
        # Simulate what iter_lines(delimiter="\n") returns for \r\n content
        response.iter_lines = Mock(return_value=iter(["Name,Email\r", "John,john@test.com\r"]))
        records = list(self.decoder.decode(response))
        assert records == [{"Name": "John", "Email": "john@test.com"}]

    def test_decode_unicode_line_separator_not_split(self):
        """Verify Unicode line separator \u2028 inside a field does not cause row splitting."""
        # With delimiter="\n", iter_lines won't split on \u2028
        response = Mock()
        response.encoding = None
        # Simulate a field containing \u2028 — it should stay within the same row
        response.iter_lines = Mock(return_value=iter(["Name,Description", 'John,"Line1\u2028Line2"']))
        records = list(self.decoder.decode(response))
        assert len(records) == 1
        assert records[0]["Name"] == "John"
        assert "\u2028" in records[0]["Description"]


class TestMarketoRecordTransformation:
    def setup_method(self):
        self.transformation = MarketoRecordTransformation(config={}, parameters={})

    def test_flatten_attributes_json_string(self):
        record = {"id": 1, "attributes": '{"Campaign Run ID": "123", "Choice Number": "5"}'}
        self.transformation.transform(record)
        assert "attributes" not in record
        assert record["campaign_run_id"] == "123"
        assert record["choice_number"] == "5"

    def test_flatten_attributes_dict(self):
        record = {"id": 1, "attributes": {"Some Key": "value"}}
        self.transformation.transform(record)
        assert "attributes" not in record
        assert record["some_key"] == "value"

    def test_no_attributes(self):
        record = {"id": 1, "name": "test"}
        self.transformation.transform(record)
        assert record == {"id": 1, "name": "test"}

    def test_invalid_attributes_json(self):
        record = {"id": 1, "attributes": "not-valid-json"}
        self.transformation.transform(record)
        assert "attributes" not in record

    def test_type_coercion_with_schema_loader(self):
        """Verify that format_value() is called for every field when a schema_loader is provided."""
        mock_loader = Mock()
        mock_loader.get_json_schema.return_value = {
            "properties": {
                "id": {"type": ["integer", "null"]},
                "score": {"type": ["number", "null"]},
                "is_active": {"type": ["boolean", "null"]},
                "name": {"type": ["string", "null"]},
            }
        }
        transformation = MarketoRecordTransformation(config={}, parameters={}, schema_loader=mock_loader)
        record = {"id": "42", "score": "3.14", "is_active": "true", "name": "test"}
        transformation.transform(record)
        assert record["id"] == 42
        assert record["score"] == 3.14
        assert record["is_active"] is True
        assert record["name"] == "test"

    def test_type_coercion_null_values(self):
        """Verify null/empty CSV values are coerced to None."""
        mock_loader = Mock()
        mock_loader.get_json_schema.return_value = {
            "properties": {
                "id": {"type": ["integer", "null"]},
                "name": {"type": ["string", "null"]},
            }
        }
        transformation = MarketoRecordTransformation(config={}, parameters={}, schema_loader=mock_loader)
        record = {"id": "null", "name": ""}
        transformation.transform(record)
        assert record["id"] is None
        assert record["name"] is None

    def test_type_coercion_without_schema_loader(self):
        """Without a schema_loader, values should remain as raw strings."""
        transformation = MarketoRecordTransformation(config={}, parameters={})
        record = {"id": "42", "score": "3.14"}
        transformation.transform(record)
        assert record["id"] == "42"
        assert record["score"] == "3.14"

    def test_type_coercion_with_attributes_flattening(self):
        """Verify that both attribute flattening and type coercion work together."""
        mock_loader = Mock()
        mock_loader.get_json_schema.return_value = {
            "properties": {
                "id": {"type": ["integer", "null"]},
                "campaign_run_id": {"type": ["integer", "null"]},
            }
        }
        transformation = MarketoRecordTransformation(config={}, parameters={}, schema_loader=mock_loader)
        record = {"id": "1", "attributes": '{"Campaign Run ID": "123"}'}
        transformation.transform(record)
        assert record["id"] == 1
        assert record["campaign_run_id"] == 123

    def test_schema_loader_error_falls_back_gracefully(self):
        """If schema_loader raises, values should pass through as raw strings."""
        mock_loader = Mock()
        mock_loader.get_json_schema.side_effect = RuntimeError("API unavailable")
        transformation = MarketoRecordTransformation(config={}, parameters={}, schema_loader=mock_loader)
        record = {"id": "42"}
        transformation.transform(record)
        assert record["id"] == "42"


class TestMarketoActivitySchemaLoader:
    def test_basic_schema(self):
        loader = MarketoActivitySchemaLoader(config={}, parameters={})
        schema = loader.get_json_schema()
        assert "marketoGUID" in schema["properties"]
        assert "leadId" in schema["properties"]
        assert "activityDate" in schema["properties"]

    def test_schema_with_attributes(self):
        attrs = json.dumps(
            [
                {"name": "Campaign Run ID", "dataType": "integer"},
                {"name": "Has Predictive", "dataType": "boolean"},
            ]
        )
        loader = MarketoActivitySchemaLoader(config={}, parameters={}, activity_attributes=attrs)
        schema = loader.get_json_schema()
        assert "campaign_run_id" in schema["properties"]
        assert schema["properties"]["campaign_run_id"]["type"] == ["integer", "null"]
        assert schema["properties"]["has_predictive"]["type"] == ["boolean", "null"]


class TestMarketoBulkExportCreationRequester:
    def _make_requester(self, **kwargs):
        config = {"domain_url": "https://test.mktorest.com", "client_id": "id", "client_secret": "secret"}
        defaults = {
            "config": config,
            "parameters": {},
            "create_requester": MagicMock(),
            "enqueue_requester": MagicMock(),
            "include_fields_from_describe": False,
        }
        defaults.update(kwargs)
        return MarketoBulkExportCreationRequester(**defaults)

    def test_quota_error_raises(self):
        response_json = {"errors": [{"code": "1029", "message": "Export daily quota 500MB exceeded"}]}
        with pytest.raises(AirbyteTracedException) as exc_info:
            MarketoBulkExportCreationRequester._check_quota_error(response_json, json.dumps(response_json))
        assert "quota" in exc_info.value.message.lower()

    def test_no_quota_error(self):
        response_json = {"result": [{"exportId": "abc"}], "success": True}
        MarketoBulkExportCreationRequester._check_quota_error(response_json, json.dumps(response_json))

    def test_build_create_body_basic(self):
        requester = self._make_requester()
        stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-31T00:00:00Z"})
        body = requester._build_create_body(stream_slice)
        assert body["format"] == "CSV"
        assert "filter" in body
        assert body["filter"]["createdAt"]["startAt"] == "2024-01-01T00:00:00Z"

    def test_build_create_body_with_activity_type_id_field(self):
        """Verify activity_type_id field on requester is used for filtering."""
        requester = self._make_requester(activity_type_id="6")
        stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-31T00:00:00Z"})
        body = requester._build_create_body(stream_slice)
        assert body["filter"]["activityTypeIds"] == [6]

    def test_build_create_body_without_activity_type_id(self):
        """Without activity_type_id, no activityTypeIds filter should be present."""
        requester = self._make_requester()
        stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-31T00:00:00Z"})
        body = requester._build_create_body(stream_slice)
        assert "activityTypeIds" not in body.get("filter", {})

    def test_build_create_body_placeholder_activity_type_id_ignored(self):
        """Placeholder activity_type_id should be ignored (not resolved to int)."""
        requester = self._make_requester(activity_type_id="placeholder_activity_type_id")
        stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-31T00:00:00Z"})
        body = requester._build_create_body(stream_slice)
        assert "activityTypeIds" not in body.get("filter", {})

    # -- send_request orchestration tests --

    def test_send_request_happy_path(self):
        """Full create+enqueue flow: create returns exportId, enqueue is called with it."""
        create_response = Mock()
        create_response.json.return_value = {
            "result": [{"exportId": "abc123", "status": "Created"}],
            "success": True,
        }
        create_response.text = '{"result": [{"exportId": "abc123", "status": "Created"}]}'

        mock_create = MagicMock()
        mock_create.send_request.return_value = create_response
        mock_enqueue = MagicMock()

        requester = self._make_requester(
            create_requester=mock_create,
            enqueue_requester=mock_enqueue,
        )
        stream_slice = StreamSlice(
            partition={},
            cursor_slice={"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-31T00:00:00Z"},
        )
        result = requester.send_request(stream_slice=stream_slice)

        assert result is create_response
        mock_create.send_request.assert_called_once()
        mock_enqueue.send_request.assert_called_once()
        enqueue_call = mock_enqueue.send_request.call_args
        enqueue_slice = enqueue_call.kwargs.get("stream_slice")
        assert enqueue_slice.extra_fields["export_id"] == "abc123"

    def test_send_request_no_result_skips_enqueue(self):
        """When create response has no 'result', enqueue should not be called."""
        create_response = Mock()
        create_response.json.return_value = {"success": True}
        create_response.text = '{"success": true}'
        mock_create = MagicMock()
        mock_create.send_request.return_value = create_response
        mock_enqueue = MagicMock()

        requester = self._make_requester(
            create_requester=mock_create,
            enqueue_requester=mock_enqueue,
        )
        result = requester.send_request(stream_slice=StreamSlice(partition={}, cursor_slice={}))
        assert result is create_response
        mock_enqueue.send_request.assert_not_called()

    def test_send_request_returns_none_when_create_fails(self):
        """When create returns None, send_request returns None and enqueue is skipped."""
        mock_create = MagicMock()
        mock_create.send_request.return_value = None
        mock_enqueue = MagicMock()

        requester = self._make_requester(
            create_requester=mock_create,
            enqueue_requester=mock_enqueue,
        )
        result = requester.send_request(stream_slice=StreamSlice(partition={}, cursor_slice={}))
        assert result is None
        mock_enqueue.send_request.assert_not_called()

    def test_send_request_unexpected_status_skips_enqueue(self):
        """When create response has unexpected status, enqueue should not be called."""
        create_response = Mock()
        create_response.json.return_value = {
            "result": [{"exportId": "abc123", "status": "Failed"}],
            "success": True,
        }
        create_response.text = '{"result": [{"exportId": "abc123", "status": "Failed"}]}'
        mock_create = MagicMock()
        mock_create.send_request.return_value = create_response
        mock_enqueue = MagicMock()

        requester = self._make_requester(
            create_requester=mock_create,
            enqueue_requester=mock_enqueue,
        )
        result = requester.send_request(stream_slice=StreamSlice(partition={}, cursor_slice={}))
        assert result is create_response
        mock_enqueue.send_request.assert_not_called()

    # -- _get_export_fields tests --

    @patch("components.requests.get")
    def test_get_export_fields_success_and_caching(self, mock_get):
        """Verify describe fields are fetched and cached."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": [
                {"rest": {"name": "firstName"}, "dataType": "string"},
                {"rest": {"name": "lastName"}, "dataType": "string"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_auth = MagicMock()
        mock_auth.get_authenticator.return_value.get_auth_header.return_value = {"Authorization": "Bearer test"}
        requester = self._make_requester(
            create_requester=mock_auth,
            include_fields_from_describe=True,
        )

        fields = requester._get_export_fields()
        assert fields == ["firstName", "lastName"]

        # Second call should use cache (no additional HTTP call)
        fields2 = requester._get_export_fields()
        assert fields2 == ["firstName", "lastName"]
        assert mock_get.call_count == 1  # Only one HTTP call

    @patch("components.requests.get")
    def test_get_export_fields_http_error_returns_none(self, mock_get):
        """Verify graceful fallback on HTTP error."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        mock_auth = MagicMock()
        mock_auth.get_authenticator.return_value.get_auth_header.return_value = {}
        requester = self._make_requester(
            create_requester=mock_auth,
            include_fields_from_describe=True,
        )
        fields = requester._get_export_fields()
        assert fields is None

    def test_get_export_fields_disabled_returns_none(self):
        """When include_fields_from_describe is False, returns None without HTTP call."""
        requester = self._make_requester(include_fields_from_describe=False)
        fields = requester._get_export_fields()
        assert fields is None


class TestMarketoLeadsSchemaLoader:
    @patch("components.requests.get")
    def test_schema_with_custom_fields(self, mock_get):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "test_token"}
        token_response.raise_for_status = Mock()
        describe_response = Mock()
        describe_response.json.return_value = {
            "result": [
                {"id": 100, "displayName": "Custom Score", "dataType": "score", "rest": {"name": "customScore__c"}},
                {"id": 101, "displayName": "Custom Date", "dataType": "date", "rest": {"name": "customDate__c"}},
            ]
        }
        describe_response.raise_for_status = Mock()
        mock_get.side_effect = [token_response, describe_response]
        loader = MarketoLeadsSchemaLoader(
            config={"domain_url": "https://test.mktorest.com", "client_id": "id", "client_secret": "secret"},
            parameters={},
        )
        schema = loader.get_json_schema()
        assert "customScore__c" in schema["properties"]
        assert schema["properties"]["customScore__c"]["type"] == ["integer", "null"]
        assert "customDate__c" in schema["properties"]
        assert schema["properties"]["customDate__c"]["format"] == "date"

    @patch("components.requests.get")
    def test_schema_fallback_on_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection failed")
        loader = MarketoLeadsSchemaLoader(
            config={"domain_url": "https://test.mktorest.com", "client_id": "id", "client_secret": "secret"},
            parameters={},
        )
        schema = loader.get_json_schema()
        assert schema["type"] == ["null", "object"]
        assert "properties" in schema
