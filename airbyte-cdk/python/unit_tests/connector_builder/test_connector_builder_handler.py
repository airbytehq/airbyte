#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from unittest import mock
from unittest.mock import patch

import connector_builder
import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from connector_builder.connector_builder_handler import resolve_manifest
from connector_builder.main import handle_connector_builder_request, handle_request, read_stream
from connector_builder.models import StreamRead, StreamReadSlicesInner, StreamReadSlicesInnerPagesInner
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
                "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
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
    "__test_read_config": {
        "max_pages_per_slice": 2,
        "max_slices": 5,
        "max_records": 10
    }
}

DUMMY_CATALOG = {
    "streams": [
        {
            "stream": {
                "name": "dummy_stream",
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {}
                },
                "supported_sync_modes": ["full_refresh"],
                "source_defined_cursor": False
            },
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite"
        }
    ]
}

CONFIGURED_CATALOG = {
    "streams": [
        {
            "stream": {
                "name": _stream_name,
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {}
                },
                "supported_sync_modes": ["full_refresh"],
                "source_defined_cursor": False
            },
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite"
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
    config["__command"] = "resolve_manifest"
    source = ManifestDeclarativeSource(MANIFEST)
    resolved_manifest = handle_connector_builder_request(source, config, create_configured_catalog("dummy_stream"))

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
                    "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
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
    stream_read = StreamRead(logs=[{"message": "here be a log message"}],
                             slices=[StreamReadSlicesInner(pages=[
                                 StreamReadSlicesInnerPagesInner(records=[real_record], request=None, response=None)],
                                 slice_descriptor=None, state=None)
                             ],
                             test_read_limit_reached=False, inferred_schema=None)

    expected_airbyte_message = AirbyteMessage(type=MessageType.RECORD,
                                              record=AirbyteRecordMessage(stream=_stream_name, data={
                                                  "logs": [{"message": "here be a log message"}],
                                                  "slices": [{
                                                      "pages": [{"records": [real_record], "request": None, "response": None}],
                                                      "slice_descriptor": None,
                                                      "state": None
                                                  }],
                                                  "test_read_limit_reached": False,
                                                  "inferred_schema": None
                                              }, emitted_at=1))
    with patch("connector_builder.message_grouper.MessageGrouper.get_message_groups", return_value=stream_read):
        output_record = handle_connector_builder_request(source, config, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG))
        output_record.record.emitted_at = 1
        assert output_record == expected_airbyte_message


def test_read_returns_error_response():
    class MockManifestDeclarativeSource:
        def read(self, logger, config, catalog, state):
            raise ValueError

    source = MockManifestDeclarativeSource()
    response = read_stream(source, TEST_READ_CONFIG, ConfiguredAirbyteCatalog.parse_obj(CONFIGURED_CATALOG))
    assert "Error reading" in response.trace.error.message


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
