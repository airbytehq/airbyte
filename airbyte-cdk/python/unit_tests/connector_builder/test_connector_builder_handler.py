#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import dataclasses
import json
import logging
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
import requests
from airbyte_cdk import connector_builder
from airbyte_cdk.connector_builder.connector_builder_handler import (
    DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE,
    DEFAULT_MAXIMUM_NUMBER_OF_SLICES,
    DEFAULT_MAXIMUM_RECORDS,
    TestReadLimits,
    create_source,
    get_limits,
    resolve_manifest,
)
from airbyte_cdk.connector_builder.main import handle_connector_builder_request, handle_request, read_stream
from airbyte_cdk.connector_builder.models import LogMessage, StreamRead, StreamReadPages, StreamReadSlices
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Level,
    SyncMode,
)
from airbyte_cdk.models import Type
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.retrievers import SimpleRetrieverTestReadDecorator
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from unit_tests.connector_builder.utils import create_configured_catalog

_stream_name = "stream_with_custom_requester"
_stream_primary_key = "id"
_stream_url_base = "https://api.sendgrid.com"
_stream_options = {"name": _stream_name, "primary_key": _stream_primary_key, "url_base": _stream_url_base}
_page_size = 2

MANIFEST = {
    "version": "0.30.3",
    "definitions": {
        "retriever": {
            "paginator": {
                "type": "DefaultPaginator",
                "page_size": _page_size,
                "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                "pagination_strategy": {
                    "type": "CursorPagination",
                    "cursor_value": "{{ response._metadata.next }}",
                    "page_size": _page_size,
                },
            },
            "partition_router": {
                "type": "ListPartitionRouter",
                "values": ["0", "1", "2", "3", "4", "5", "6", "7"],
                "cursor_field": "item_id",
            },
            ""
            "requester": {
                "path": "/v3/marketing/lists",
                "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                "request_parameters": {"a_param": "10"},
            },
            "record_selector": {"extractor": {"field_path": ["result"]}},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "$parameters": _stream_options,
            "retriever": "#/definitions/retriever",
        },
    ],
    "check": {"type": "CheckStream", "stream_names": ["lists"]},
    "spec": {
        "connection_specification": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": [],
            "properties": {},
            "additionalProperties": True,
        },
        "type": "Spec",
    },
}

OAUTH_MANIFEST = {
    "version": "0.30.3",
    "definitions": {
        "retriever": {
            "paginator": {
                "type": "DefaultPaginator",
                "page_size": _page_size,
                "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                "pagination_strategy": {
                    "type": "CursorPagination",
                    "cursor_value": "{{ response._metadata.next }}",
                    "page_size": _page_size,
                },
            },
            "partition_router": {
                "type": "ListPartitionRouter",
                "values": ["0", "1", "2", "3", "4", "5", "6", "7"],
                "cursor_field": "item_id",
            },
            ""
            "requester": {
                "path": "/v3/marketing/lists",
                "authenticator": {"type": "OAuthAuthenticator", "api_token": "{{ config.apikey }}"},
                "request_parameters": {"a_param": "10"},
            },
            "record_selector": {"extractor": {"field_path": ["result"]}},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "$parameters": _stream_options,
            "retriever": "#/definitions/retriever",
        },
    ],
    "check": {"type": "CheckStream", "stream_names": ["lists"]},
    "spec": {
        "connection_specification": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": [],
            "properties": {},
            "additionalProperties": True,
        },
        "type": "Spec",
    },
}

RESOLVE_MANIFEST_CONFIG = {
    "__injected_declarative_manifest": MANIFEST,
    "__command": "resolve_manifest",
}

TEST_READ_CONFIG = {
    "__injected_declarative_manifest": MANIFEST,
    "__command": "test_read",
    "__test_read_config": {"max_pages_per_slice": 2, "max_slices": 5, "max_records": 10},
}

DUMMY_CATALOG = {
    "streams": [
        {
            "stream": {
                "name": "dummy_stream",
                "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                "supported_sync_modes": ["full_refresh"],
                "source_defined_cursor": False,
            },
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite",
        }
    ]
}

CONFIGURED_CATALOG = {
    "streams": [
        {
            "stream": {
                "name": _stream_name,
                "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                "supported_sync_modes": ["full_refresh"],
                "source_defined_cursor": False,
            },
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite",
        }
    ]
}

MOCK_RESPONSE = {
    "result": [
        {"id": 1, "name": "Nora Moon", "position": "director"},
        {"id": 2, "name": "Hae Sung Jung", "position": "cinematographer"},
        {"id": 3, "name": "Arthur Zenneranski", "position": "composer"},
    ]
}


@pytest.fixture
def valid_resolve_manifest_config_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(RESOLVE_MANIFEST_CONFIG))
    return config_file


@pytest.fixture
def valid_read_config_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(TEST_READ_CONFIG))
    return config_file


@pytest.fixture
def dummy_catalog(tmp_path):
    config_file = tmp_path / "catalog.json"
    config_file.write_text(json.dumps(DUMMY_CATALOG))
    return config_file


@pytest.fixture
def configured_catalog(tmp_path):
    config_file = tmp_path / "catalog.json"
    config_file.write_text(json.dumps(CONFIGURED_CATALOG))
    return config_file


@pytest.fixture
def invalid_config_file(tmp_path):
    invalid_config = copy.deepcopy(RESOLVE_MANIFEST_CONFIG)
    invalid_config["__command"] = "bad_command"
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(invalid_config))
    return config_file


def _mocked_send(self, request, **kwargs) -> requests.Response:
    """
    Mocks the outbound send operation to provide faster and more reliable responses compared to actual API requests
    """
    response = requests.Response()
    response.request = request
    response.status_code = 200
    response.headers = {"header": "value"}
    response_body = MOCK_RESPONSE
    response._content = json.dumps(response_body).encode("utf-8")
    return response


def test_handle_resolve_manifest(valid_resolve_manifest_config_file, dummy_catalog):
    with mock.patch.object(connector_builder.main, "handle_connector_builder_request") as patched_handle:
        handle_request(["read", "--config", str(valid_resolve_manifest_config_file), "--catalog", str(dummy_catalog)])
        assert patched_handle.call_count == 1


def test_handle_test_read(valid_read_config_file, configured_catalog):
    with mock.patch.object(connector_builder.main, "handle_connector_builder_request") as patch:
        handle_request(["read", "--config", str(valid_read_config_file), "--catalog", str(configured_catalog)])
        assert patch.call_count == 1


def test_resolve_manifest(valid_resolve_manifest_config_file):
    config = copy.deepcopy(RESOLVE_MANIFEST_CONFIG)
    command = "resolve_manifest"
    config["__command"] = command
    source = ManifestDeclarativeSource(MANIFEST)
    limits = TestReadLimits()
    resolved_manifest = handle_connector_builder_request(source, command, config, create_configured_catalog("dummy_stream"), limits)

    expected_resolved_manifest = {
        "type": "DeclarativeSource",
        "version": "0.30.3",
        "definitions": {
            "retriever": {
                "paginator": {
                    "type": "DefaultPaginator",
                    "page_size": _page_size,
                    "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                    "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                    "pagination_strategy": {
                        "type": "CursorPagination",
                        "cursor_value": "{{ response._metadata.next }}",
                        "page_size": _page_size,
                    },
                },
                "partition_router": {
                    "type": "ListPartitionRouter",
                    "values": ["0", "1", "2", "3", "4", "5", "6", "7"],
                    "cursor_field": "item_id",
                },
                "requester": {
                    "path": "/v3/marketing/lists",
                    "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                    "request_parameters": {"a_param": "10"},
                },
                "record_selector": {"extractor": {"field_path": ["result"]}},
            },
        },
        "streams": [
            {
                "type": "DeclarativeStream",
                "retriever": {
                    "type": "SimpleRetriever",
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": _page_size,
                        "page_size_option": {
                            "type": "RequestOption",
                            "inject_into": "request_parameter",
                            "field_name": "page_size",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$parameters": _stream_options,
                        },
                        "page_token_option": {
                            "type": "RequestPath",
                            "inject_into": "path",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$parameters": _stream_options,
                        },
                        "pagination_strategy": {
                            "type": "CursorPagination",
                            "cursor_value": "{{ response._metadata.next }}",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$parameters": _stream_options,
                            "page_size": _page_size,
                        },
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$parameters": _stream_options,
                    },
                    "requester": {
                        "type": "HttpRequester",
                        "path": "/v3/marketing/lists",
                        "authenticator": {
                            "type": "BearerAuthenticator",
                            "api_token": "{{ config.apikey }}",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$parameters": _stream_options,
                        },
                        "request_parameters": {"a_param": "10"},
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$parameters": _stream_options,
                    },
                    "partition_router": {
                        "type": "ListPartitionRouter",
                        "values": ["0", "1", "2", "3", "4", "5", "6", "7"],
                        "cursor_field": "item_id",
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$parameters": _stream_options,
                    },
                    "record_selector": {
                        "type": "RecordSelector",
                        "extractor": {
                            "type": "DpathExtractor",
                            "field_path": ["result"],
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$parameters": _stream_options,
                        },
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$parameters": _stream_options,
                    },
                    "name": _stream_name,
                    "primary_key": _stream_primary_key,
                    "url_base": _stream_url_base,
                    "$parameters": _stream_options,
                },
                "name": _stream_name,
                "primary_key": _stream_primary_key,
                "url_base": _stream_url_base,
                "$parameters": _stream_options,
            },
        ],
        "check": {"type": "CheckStream", "stream_names": ["lists"]},
        "spec": {
            "connection_specification": {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": [],
                "properties": {},
                "additionalProperties": True,
            },
            "type": "Spec",
        },
    }
    assert resolved_manifest.record.data["manifest"] == expected_resolved_manifest
    assert resolved_manifest.record.stream == "resolve_manifest"


def test_resolve_manifest_error_returns_error_response():
    class MockManifestDeclarativeSource:
        @property
        def resolved_manifest(self):
            raise ValueError

    source = MockManifestDeclarativeSource()
    response = resolve_manifest(source)
    assert "Error resolving manifest" in response.trace.error.message


def test_read():
    config = TEST_READ_CONFIG
    source = ManifestDeclarativeSource(MANIFEST)

    real_record = AirbyteRecordMessage(data={"id": "1234", "key": "value"}, emitted_at=1, stream=_stream_name)
    stream_read = StreamRead(
        logs=[{"message": "here be a log message"}],
        slices=[
            StreamReadSlices(
                pages=[StreamReadPages(records=[real_record], request=None, response=None)],
                slice_descriptor=None,
                state=None,
            )
        ],
        auxiliary_requests=[],
        test_read_limit_reached=False,
        inferred_schema=None,
        inferred_datetime_formats=None,
        latest_config_update={},
    )

    expected_airbyte_message = AirbyteMessage(
        type=MessageType.RECORD,
        record=AirbyteRecordMessage(
            stream=_stream_name,
            data={
                "logs": [{"message": "here be a log message"}],
                "slices": [
                    {"pages": [{"records": [real_record], "request": None, "response": None}], "slice_descriptor": None, "state": None}
                ],
                "test_read_limit_reached": False,
                "auxiliary_requests": [],
                "inferred_schema": None,
                "inferred_datetime_formats": None,
                "latest_config_update": {},
            },
            emitted_at=1,
        ),
    )
    limits = TestReadLimits()
    with patch("airbyte_cdk.connector_builder.message_grouper.MessageGrouper.get_message_groups", return_value=stream_read):
        output_record = handle_connector_builder_request(
            source, "test_read", config, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG), limits
        )
        output_record.record.emitted_at = 1
        assert output_record == expected_airbyte_message


def test_config_update():
    manifest = copy.deepcopy(MANIFEST)
    manifest["definitions"]["retriever"]["requester"]["authenticator"] = {
        "type": "OAuthAuthenticator",
        "token_refresh_endpoint": "https://oauth.endpoint.com/tokens/bearer",
        "client_id": "{{ config['credentials']['client_id'] }}",
        "client_secret": "{{ config['credentials']['client_secret'] }}",
        "refresh_token": "{{ config['credentials']['refresh_token'] }}",
        "refresh_token_updater": {},
    }
    config = copy.deepcopy(TEST_READ_CONFIG)
    config["__injected_declarative_manifest"] = manifest
    config["credentials"] = {
        "client_id": "a client id",
        "client_secret": "a client secret",
        "refresh_token": "a refresh token",
    }
    source = ManifestDeclarativeSource(manifest)

    refresh_request_response = {
        "access_token": "an updated access token",
        "refresh_token": "an updated refresh token",
        "expires_in": 3600,
    }
    with patch(
        "airbyte_cdk.sources.streams.http.requests_native_auth.SingleUseRefreshTokenOauth2Authenticator._get_refresh_access_token_response",
        return_value=refresh_request_response,
    ):
        output = handle_connector_builder_request(
            source, "test_read", config, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG), TestReadLimits()
        )
        assert output.record.data["latest_config_update"]


@patch("traceback.TracebackException.from_exception")
def test_read_returns_error_response(mock_from_exception):
    class MockManifestDeclarativeSource:
        def read(self, logger, config, catalog, state):
            raise ValueError("error_message")

        def spec(self, logger: logging.Logger) -> ConnectorSpecification:
            connector_specification = mock.Mock()
            connector_specification.connectionSpecification = {}
            return connector_specification

        @property
        def check_config_against_spec(self):
            return False

    stack_trace = "a stack trace"
    mock_from_exception.return_value = stack_trace

    source = MockManifestDeclarativeSource()
    limits = TestReadLimits()
    response = read_stream(source, TEST_READ_CONFIG, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG), limits)

    expected_stream_read = StreamRead(
        logs=[LogMessage("error_message - a stack trace", "ERROR")],
        slices=[],
        test_read_limit_reached=False,
        auxiliary_requests=[],
        inferred_schema=None,
        inferred_datetime_formats={},
        latest_config_update=None,
    )

    expected_message = AirbyteMessage(
        type=MessageType.RECORD,
        record=AirbyteRecordMessage(stream=_stream_name, data=dataclasses.asdict(expected_stream_read), emitted_at=1),
    )
    response.record.emitted_at = 1
    assert response == expected_message


@pytest.mark.parametrize(
    "command",
    [
        pytest.param("check", id="test_check_command_error"),
        pytest.param("spec", id="test_spec_command_error"),
        pytest.param("discover", id="test_discover_command_error"),
        pytest.param(None, id="test_command_is_none_error"),
        pytest.param("", id="test_command_is_empty_error"),
    ],
)
def test_invalid_protocol_command(command, valid_resolve_manifest_config_file):
    config = copy.deepcopy(RESOLVE_MANIFEST_CONFIG)
    config["__command"] = "resolve_manifest"
    with pytest.raises(SystemExit):
        handle_request([command, "--config", str(valid_resolve_manifest_config_file), "--catalog", ""])


def test_missing_command(valid_resolve_manifest_config_file):
    with pytest.raises(SystemExit):
        handle_request(["--config", str(valid_resolve_manifest_config_file), "--catalog", ""])


def test_missing_catalog(valid_resolve_manifest_config_file):
    with pytest.raises(SystemExit):
        handle_request(["read", "--config", str(valid_resolve_manifest_config_file)])


def test_missing_config(valid_resolve_manifest_config_file):
    with pytest.raises(SystemExit):
        handle_request(["read", "--catalog", str(valid_resolve_manifest_config_file)])


def test_invalid_config_command(invalid_config_file, dummy_catalog):
    with pytest.raises(ValueError):
        handle_request(["read", "--config", str(invalid_config_file), "--catalog", str(dummy_catalog)])


@pytest.fixture
def manifest_declarative_source():
    return mock.Mock(spec=ManifestDeclarativeSource, autospec=True)


def create_mock_retriever(name, url_base, path):
    http_stream = mock.Mock(spec=SimpleRetriever, autospec=True)
    http_stream.name = name
    http_stream.requester = MagicMock()
    http_stream.requester.get_url_base.return_value = url_base
    http_stream.requester.get_path.return_value = path
    http_stream._paginator_path.return_value = None
    return http_stream


def create_mock_declarative_stream(http_stream):
    declarative_stream = mock.Mock(spec=DeclarativeStream, autospec=True)
    declarative_stream.retriever = http_stream
    return declarative_stream


@pytest.mark.parametrize(
    "test_name, config, expected_max_records, expected_max_slices, expected_max_pages_per_slice",
    [
        (
            "test_no_test_read_config",
            {},
            DEFAULT_MAXIMUM_RECORDS,
            DEFAULT_MAXIMUM_NUMBER_OF_SLICES,
            DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE,
        ),
        (
            "test_no_values_set",
            {"__test_read_config": {}},
            DEFAULT_MAXIMUM_RECORDS,
            DEFAULT_MAXIMUM_NUMBER_OF_SLICES,
            DEFAULT_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE,
        ),
        ("test_values_are_set", {"__test_read_config": {"max_slices": 1, "max_pages_per_slice": 2, "max_records": 3}}, 3, 1, 2),
    ],
)
def test_get_limits(test_name, config, expected_max_records, expected_max_slices, expected_max_pages_per_slice):
    limits = get_limits(config)
    assert limits.max_records == expected_max_records
    assert limits.max_pages_per_slice == expected_max_pages_per_slice
    assert limits.max_slices == expected_max_slices


def test_create_source():
    max_records = 3
    max_pages_per_slice = 2
    max_slices = 1
    limits = TestReadLimits(max_records, max_pages_per_slice, max_slices)

    config = {"__injected_declarative_manifest": MANIFEST}

    source = create_source(config, limits)

    assert isinstance(source, ManifestDeclarativeSource)
    assert source._constructor._limit_pages_fetched_per_slice == limits.max_pages_per_slice
    assert source._constructor._limit_slices_fetched == limits.max_slices
    assert source.streams(config={})[0].retriever.requester.max_retries == 0


def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def _create_request():
    url = "https://example.com/api"
    headers = {"Content-Type": "application/json"}
    return requests.Request("POST", url, headers=headers, json={"key": "value"}).prepare()


def _create_response(body, request):
    response = requests.Response()
    response.status_code = 200
    response._content = bytes(json.dumps(body), "utf-8")
    response.headers["Content-Type"] = "application/json"
    response.request = request
    return response


def _create_page_response(response_body):
    request = _create_request()
    return _create_response(response_body, request)


@patch.object(
    requests.Session,
    "send",
    side_effect=(
        _create_page_response({"result": [{"id": 0}, {"id": 1}], "_metadata": {"next": "next"}}),
        _create_page_response({"result": [{"id": 2}], "_metadata": {"next": "next"}}),
    )
    * 10,
)
def test_read_source(mock_http_stream):
    """
    This test sort of acts as an integration test for the connector builder.

    Each slice has two pages
    The first page has two records
    The second page one record

    The response._metadata.next field in the first page tells the paginator to fetch the next page.
    """
    max_records = 100
    max_pages_per_slice = 2
    max_slices = 3
    limits = TestReadLimits(max_records, max_pages_per_slice, max_slices)

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=_stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    config = {"__injected_declarative_manifest": MANIFEST}

    source = create_source(config, limits)

    output_data = read_stream(source, config, catalog, limits).record.data
    slices = output_data["slices"]

    assert len(slices) == max_slices
    for s in slices:
        pages = s["pages"]
        assert len(pages) == max_pages_per_slice

        first_page, second_page = pages[0], pages[1]
        assert len(first_page["records"]) == _page_size
        assert len(second_page["records"]) == 1

    streams = source.streams(config)
    for s in streams:
        assert isinstance(s.retriever, SimpleRetrieverTestReadDecorator)


@patch.object(
    requests.Session,
    "send",
    side_effect=(
        _create_page_response({"result": [{"id": 0}, {"id": 1}], "_metadata": {"next": "next"}}),
        _create_page_response({"result": [{"id": 2}], "_metadata": {"next": "next"}}),
    ),
)
def test_read_source_single_page_single_slice(mock_http_stream):
    max_records = 100
    max_pages_per_slice = 1
    max_slices = 1
    limits = TestReadLimits(max_records, max_pages_per_slice, max_slices)

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=_stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    config = {"__injected_declarative_manifest": MANIFEST}

    source = create_source(config, limits)

    output_data = read_stream(source, config, catalog, limits).record.data
    slices = output_data["slices"]

    assert len(slices) == max_slices
    for s in slices:
        pages = s["pages"]
        assert len(pages) == max_pages_per_slice

        first_page = pages[0]
        assert len(first_page["records"]) == _page_size

    streams = source.streams(config)
    for s in streams:
        assert isinstance(s.retriever, SimpleRetrieverTestReadDecorator)


@pytest.mark.parametrize(
    "deployment_mode, url_base, expected_error",
    [
        pytest.param("CLOUD", "https://airbyte.com/api/v1/characters", None, id="test_cloud_read_with_public_endpoint"),
        pytest.param("CLOUD", "https://10.0.27.27", "AirbyteTracedException", id="test_cloud_read_with_private_endpoint"),
        pytest.param("CLOUD", "https://localhost:80/api/v1/cast", "AirbyteTracedException", id="test_cloud_read_with_localhost"),
        pytest.param("CLOUD", "http://unsecured.protocol/api/v1", "InvalidSchema", id="test_cloud_read_with_unsecured_endpoint"),
        pytest.param("CLOUD", "https://domainwithoutextension", "Invalid URL", id="test_cloud_read_with_invalid_url_endpoint"),
        pytest.param("OSS", "https://airbyte.com/api/v1/", None, id="test_oss_read_with_public_endpoint"),
        pytest.param("OSS", "https://10.0.27.27/api/v1/", None, id="test_oss_read_with_private_endpoint"),
    ],
)
@patch.object(requests.Session, "send", _mocked_send)
def test_handle_read_external_requests(deployment_mode, url_base, expected_error):
    """
    This test acts like an integration test for the connector builder when it receives Test Read requests.

    The scenario being tested is whether requests should be denied if they are done on an unsecure channel or are made to internal
    endpoints when running on Cloud or OSS deployments
    """

    limits = TestReadLimits(max_records=100, max_pages_per_slice=1, max_slices=1)

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=_stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    test_manifest = MANIFEST
    test_manifest["streams"][0]["$parameters"]["url_base"] = url_base
    config = {"__injected_declarative_manifest": test_manifest}

    source = create_source(config, limits)

    with mock.patch.dict(os.environ, {"DEPLOYMENT_MODE": deployment_mode}, clear=False):
        output_data = read_stream(source, config, catalog, limits).record.data
        if expected_error:
            assert len(output_data["logs"]) > 0, "Expected at least one log message with the expected error"
            error_message = output_data["logs"][0]
            assert error_message["level"] == "ERROR"
            assert expected_error in error_message["message"]
        else:
            page_records = output_data["slices"][0]["pages"][0]
            assert len(page_records) == len(MOCK_RESPONSE["result"])


@pytest.mark.parametrize(
    "deployment_mode, token_url, expected_error",
    [
        pytest.param("CLOUD", "https://airbyte.com/tokens/bearer", None, id="test_cloud_read_with_public_endpoint"),
        pytest.param("CLOUD", "https://10.0.27.27/tokens/bearer", "AirbyteTracedException", id="test_cloud_read_with_private_endpoint"),
        pytest.param("CLOUD", "http://unsecured.protocol/tokens/bearer", "InvalidSchema", id="test_cloud_read_with_unsecured_endpoint"),
        pytest.param("CLOUD", "https://domainwithoutextension", "Invalid URL", id="test_cloud_read_with_invalid_url_endpoint"),
        pytest.param("OSS", "https://airbyte.com/tokens/bearer", None, id="test_oss_read_with_public_endpoint"),
        pytest.param("OSS", "https://10.0.27.27/tokens/bearer", None, id="test_oss_read_with_private_endpoint"),
    ],
)
@patch.object(requests.Session, "send", _mocked_send)
def test_handle_read_external_oauth_request(deployment_mode, token_url, expected_error):
    """
    This test acts like an integration test for the connector builder when it receives Test Read requests.

    The scenario being tested is whether requests should be denied if they are done on an unsecure channel or are made to internal
    endpoints when running on Cloud or OSS deployments
    """

    limits = TestReadLimits(max_records=100, max_pages_per_slice=1, max_slices=1)

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=_stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    oauth_authenticator_config: dict[str, str] = {
        "type": "OAuthAuthenticator",
        "token_refresh_endpoint": token_url,
        "client_id": "greta",
        "client_secret": "teo",
        "refresh_token": "john",
    }

    test_manifest = MANIFEST
    test_manifest["definitions"]["retriever"]["requester"]["authenticator"] = oauth_authenticator_config
    config = {"__injected_declarative_manifest": test_manifest}

    source = create_source(config, limits)

    with mock.patch.dict(os.environ, {"DEPLOYMENT_MODE": deployment_mode}, clear=False):
        output_data = read_stream(source, config, catalog, limits).record.data
        if expected_error:
            assert len(output_data["logs"]) > 0, "Expected at least one log message with the expected error"
            error_message = output_data["logs"][0]
            assert error_message["level"] == "ERROR"
            assert expected_error in error_message["message"]
