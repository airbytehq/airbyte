#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest

import connector_builder.connector_builder_handler
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from connector_builder.connector_builder_handler import resolve_manifest, get_connector_builder_request_handler
from unit_tests.connector_builder.utils import create_configured_catalog
from functools import partial

_stream_name = "stream_with_custom_requester"
_stream_primary_key = "id"
_stream_url_base = "https://api.sendgrid.com"
_stream_options = {"name": _stream_name, "primary_key": _stream_primary_key, "url_base": _stream_url_base}

MANIFEST = {
    "version": "version",
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

CONFIG = {
    "__injected_declarative_manifest": MANIFEST,
}

TEST_READ_CONFIG = {
    "__injected_declarative_manifest": MANIFEST,
    "__test_read_config": {
        "max_records": 10
    }
}


def test_resolve_manifest():
    source = ManifestDeclarativeSource(MANIFEST)
    resolved_manifest = resolve_manifest(source)

    expected_resolved_manifest = {
        "type": "DeclarativeSource",
        "version": "version",
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


@pytest.mark.parametrize("test_name, config, configured_catalog, expected_result",
                         [
                             ("test_resolve_manifest_is_connector_builder_request", CONFIG, create_configured_catalog("resolve_manifest"), connector_builder.connector_builder_handler.resolve_manifest),
                             ("test_list_streams_is_connector_builder_request", CONFIG, create_configured_catalog("list_streams"), connector_builder.connector_builder_handler.list_streams),
                             ("test_regular_stream_is_not_connector_builder_request", CONFIG, create_configured_catalog("my_stream"), None),
                             ("test_regular_stream_with_test_read_config_is_connector_builder_request", TEST_READ_CONFIG,
                              create_configured_catalog("my_stream"),
                              partial(connector_builder.connector_builder_handler.read_stream, config=TEST_READ_CONFIG,
                                      configured_catalog=create_configured_catalog("my_stream"))),
                         ])
def test_get_connector_builder_request(test_name, config, configured_catalog, expected_result):
    result = get_connector_builder_request_handler(config, configured_catalog)
    if isinstance(expected_result, partial):
        assert partial_functions_equal(expected_result, result)
    else:
        assert result == expected_result


def partial_functions_equal(func1, func2):
    if not (isinstance(func1, partial) and isinstance(func2, partial)):
        return False
    are_equal = all([getattr(func1, attr) == getattr(func2, attr) for attr in ['func', 'args', 'keywords']])
    return are_equal
