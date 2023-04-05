#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import dataclasses
import json
from unittest import mock
from unittest.mock import patch

import pytest
from airbyte_cdk import connector_builder
from airbyte_cdk.connector_builder.connector_builder_handler import list_streams, resolve_manifest
from airbyte_cdk.connector_builder.main import handle_connector_builder_request, handle_request, read_stream
from airbyte_cdk.connector_builder.models import LogMessage, StreamRead, StreamReadSlicesInner, StreamReadSlicesInnerPagesInner
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from unit_tests.connector_builder.utils import create_configured_catalog

_stream_name = "stream_with_custom_requester"
_stream_primary_key = "id"
_stream_url_base = "https://api.sendgrid.com"
_stream_options = {"name": _stream_name, "primary_key": _stream_primary_key, "url_base": _stream_url_base}

MANIFEST = {
    "version": "0.30.3",
    "definitions": {
        "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
        "retriever": {
            "paginator": {
                "type": "DefaultPaginator",
                "page_size": 10,
                "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}", "page_size": 10},
            },
            "requester": {
                "path": "/v3/marketing/lists",
                "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                "request_parameters": {"page_size": "10"},
            },
            "record_selector": {"extractor": {"field_path": ["result"]}},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "$parameters": _stream_options,
            "schema_loader": {"$ref": "#/definitions/schema_loader"},
            "retriever": "#/definitions/retriever",
        },
    ],
    "check": {"type": "CheckStream", "stream_names": ["lists"]},
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


def test_handle_resolve_manifest(valid_resolve_manifest_config_file, dummy_catalog):
    with mock.patch.object(connector_builder.main, "handle_connector_builder_request") as patch:
        handle_request(["read", "--config", str(valid_resolve_manifest_config_file), "--catalog", str(dummy_catalog)])
        assert patch.call_count == 1


def test_handle_test_read(valid_read_config_file, configured_catalog):
    with mock.patch.object(connector_builder.main, "handle_connector_builder_request") as patch:
        handle_request(["read", "--config", str(valid_read_config_file), "--catalog", str(configured_catalog)])
        assert patch.call_count == 1


def test_resolve_manifest(valid_resolve_manifest_config_file):
    config = copy.deepcopy(RESOLVE_MANIFEST_CONFIG)
    command = "resolve_manifest"
    config["__command"] = command
    source = ManifestDeclarativeSource(MANIFEST)
    resolved_manifest = handle_connector_builder_request(source, command, config, create_configured_catalog("dummy_stream"))

    expected_resolved_manifest = {
        "type": "DeclarativeSource",
        "version": "0.30.3",
        "definitions": {
            "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
            "retriever": {
                "paginator": {
                    "type": "DefaultPaginator",
                    "page_size": 10,
                    "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                    "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                    "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}", "page_size": 10},
                },
                "requester": {
                    "path": "/v3/marketing/lists",
                    "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                    "request_parameters": {"page_size": "10"},
                },
                "record_selector": {"extractor": {"field_path": ["result"]}},
            },
        },
        "streams": [
            {
                "type": "DeclarativeStream",
                "schema_loader": {
                    "type": "JsonFileSchemaLoader",
                    "name": "{{ options.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    "primary_key": _stream_primary_key,
                    "url_base": _stream_url_base,
                    "$parameters": _stream_options,
                },
                "retriever": {
                    "type": "SimpleRetriever",
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
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
                            "page_size": 10,
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
                        "request_parameters": {"page_size": "10"},
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
            StreamReadSlicesInner(
                pages=[StreamReadSlicesInnerPagesInner(records=[real_record], request=None, response=None)],
                slice_descriptor=None,
                state=None,
            )
        ],
        test_read_limit_reached=False,
        inferred_schema=None,
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
                "inferred_schema": None,
            },
            emitted_at=1,
        ),
    )
    with patch("airbyte_cdk.connector_builder.message_grouper.MessageGrouper.get_message_groups", return_value=stream_read):
        output_record = handle_connector_builder_request(
            source, "test_read", config, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG)
        )
        output_record.record.emitted_at = 1
        assert output_record == expected_airbyte_message


@patch("traceback.TracebackException.from_exception")
def test_read_returns_error_response(mock_from_exception):
    class MockManifestDeclarativeSource:
        def read(self, logger, config, catalog, state):
            raise ValueError("error_message")

    stack_trace = "a stack trace"
    mock_from_exception.return_value = stack_trace

    source = MockManifestDeclarativeSource()
    response = read_stream(source, TEST_READ_CONFIG, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG))

    expected_stream_read = StreamRead(logs=[LogMessage("error_message - a stack trace", "ERROR")],
                                      slices=[StreamReadSlicesInner(
                                          pages=[StreamReadSlicesInnerPagesInner(records=[], request=None, response=None)],
                                          slice_descriptor=None, state=None)],
                                      test_read_limit_reached=False,
                                      inferred_schema=None)

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
    config["__command"] = "list_streams"
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


def test_list_streams(manifest_declarative_source):
    manifest_declarative_source.streams.return_value = [
        create_mock_declarative_stream(create_mock_http_stream("a name", "https://a-url-base.com", "a-path")),
        create_mock_declarative_stream(create_mock_http_stream("another name", "https://another-url-base.com", "another-path")),
    ]

    result = list_streams(manifest_declarative_source, {})

    assert result.type == MessageType.RECORD
    assert result.record.stream == "list_streams"
    assert result.record.data == {
        "streams": [
            {"name": "a name", "url": "https://a-url-base.com/a-path"},
            {"name": "another name", "url": "https://another-url-base.com/another-path"},
        ]
    }


def test_given_stream_is_not_declarative_stream_when_list_streams_then_return_exception_message(manifest_declarative_source):
    manifest_declarative_source.streams.return_value = [mock.Mock(spec=Stream)]

    error_message = list_streams(manifest_declarative_source, {})

    assert error_message.type == MessageType.TRACE
    assert "Error listing streams." == error_message.trace.error.message
    assert "A declarative source should only contain streams of type DeclarativeStream" in error_message.trace.error.internal_message


def test_given_declarative_stream_retriever_is_not_http_when_list_streams_then_return_exception_message(manifest_declarative_source):
    declarative_stream = mock.Mock(spec=DeclarativeStream)
    # `spec=DeclarativeStream` is needed for `isinstance` work but `spec` does not expose dataclasses fields, so we create one ourselves
    declarative_stream.retriever = mock.Mock()
    manifest_declarative_source.streams.return_value = [declarative_stream]

    error_message = list_streams(manifest_declarative_source, {})

    assert error_message.type == MessageType.TRACE
    assert "Error listing streams." == error_message.trace.error.message
    assert "A declarative stream should only have a retriever of type HttpStream" in error_message.trace.error.internal_message


def test_given_unexpected_error_when_list_streams_then_return_exception_message(manifest_declarative_source):
    manifest_declarative_source.streams.side_effect = Exception("unexpected error")

    error_message = list_streams(manifest_declarative_source, {})

    assert error_message.type == MessageType.TRACE
    assert "Error listing streams." == error_message.trace.error.message
    assert "unexpected error" == error_message.trace.error.internal_message


def test_list_streams_integration_test():
    config = copy.deepcopy(RESOLVE_MANIFEST_CONFIG)
    command = "list_streams"
    config["__command"] = command
    source = ManifestDeclarativeSource(MANIFEST)

    list_streams = handle_connector_builder_request(source, command, config, None)

    assert list_streams.record.data == {
        "streams": [{"name": "stream_with_custom_requester", "url": "https://api.sendgrid.com/v3/marketing/lists"}]
    }


def create_mock_http_stream(name, url_base, path):
    http_stream = mock.Mock(spec=HttpStream, autospec=True)
    http_stream.name = name
    http_stream.url_base = url_base
    http_stream.path.return_value = path
    return http_stream


def create_mock_declarative_stream(http_stream):
    declarative_stream = mock.Mock(spec=DeclarativeStream, autospec=True)
    declarative_stream.retriever = http_stream
    return declarative_stream
