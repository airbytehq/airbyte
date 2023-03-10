#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Iterator
from unittest.mock import MagicMock

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from connector_builder.connector_builder_handler import read_stream, resolve_manifest

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
    "__command": "resolve_manifest",
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
    assert resolved_manifest.data["manifest"] == expected_resolved_manifest


def test_resolve_manifest_error_returns_error_response():
    class MockManifestDeclarativeSource:
        @property
        def resolved_manifest(self):
            raise ValueError

    source = MockManifestDeclarativeSource()
    response = resolve_manifest(source)
    assert "Error resolving manifest" in response.trace.error.message
