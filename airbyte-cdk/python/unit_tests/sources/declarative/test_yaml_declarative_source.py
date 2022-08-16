#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import os
import tempfile
import unittest

import pytest
from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from jsonschema import ValidationError


class TestYamlDeclarativeSource(unittest.TestCase):
    def test_source_is_created_if_toplevel_fields_are_known(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
          retriever:
            paginator:
              type: "LimitPaginator"
              page_size: 10
              limit_option:
                inject_into: request_parameter
                field_name: page_size
              page_token_option:
                inject_into: path
              pagination_strategy:
                type: "CursorPagination"
                cursor_value: "{{ response._metadata.next }}"
            requester:
              path: "/v3/marketing/lists"
              authenticator:
                type: "BearerAuthenticator"
                api_token: "{{ config.apikey }}"
              request_parameters:
                page_size: 10
            record_selector:
              extractor:
                field_pointer: ["result"]
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "*ref(definitions.schema_loader)"
            retriever: "*ref(definitions.retriever)"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        YamlDeclarativeSource(temporary_file.filename)

    def test_source_is_not_created_if_toplevel_fields_are_unknown(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
          retriever:
            paginator:
              type: "LimitPaginator"
              page_size: 10
              limit_option:
                inject_into: request_parameter
                field_name: page_size
              page_token_option:
                inject_into: path
              pagination_strategy:
                type: "CursorPagination"
                cursor_value: "{{ response._metadata.next }}"
            requester:
              path: "/v3/marketing/lists"
              authenticator:
                type: "BearerAuthenticator"
                api_token: "{{ config.apikey }}"
              request_parameters:
                page_size: 10
            record_selector:
              extractor:
                field_pointer: ["result"]
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "*ref(definitions.schema_loader)"
            retriever: "*ref(definitions.retriever)"
        check:
          type: CheckStream
          stream_names: ["lists"]
        not_a_valid_field: "error"
        """
        temporary_file = TestFileContent(content)
        with self.assertRaises(InvalidConnectorDefinitionException):
            YamlDeclarativeSource(temporary_file.filename)

    def test_source_missing_checker_fails_validation(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
          retriever:
            paginator:
              type: "LimitPaginator"
              page_size: 10
              limit_option:
                inject_into: request_parameter
                field_name: page_size
              page_token_option:
                inject_into: path
              pagination_strategy:
                type: "CursorPagination"
                cursor_value: "{{ response._metadata.next }}"
            requester:
              path: "/v3/marketing/lists"
              authenticator:
                type: "BearerAuthenticator"
                api_token: "{{ config.apikey }}"
              request_parameters:
                page_size: 10
            record_selector:
              extractor:
                field_pointer: ["result"]
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "*ref(definitions.schema_loader)"
            retriever: "*ref(definitions.retriever)"
        check:
          type: CheckStream
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ValidationError):
            YamlDeclarativeSource(temporary_file.filename)

    def test_source_with_missing_streams_fails(self):
        content = """
        version: "version"
        definitions:
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ValidationError):
            YamlDeclarativeSource(temporary_file.filename)

    def test_source_with_missing_version_fails(self):
        content = """
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
          retriever:
            paginator:
              type: "LimitPaginator"
              page_size: 10
              limit_option:
                inject_into: request_parameter
                field_name: page_size
              page_token_option:
                inject_into: path
              pagination_strategy:
                type: "CursorPagination"
                cursor_value: "{{ response._metadata.next }}"
            requester:
              path: "/v3/marketing/lists"
              authenticator:
                type: "BearerAuthenticator"
                api_token: "{{ config.apikey }}"
              request_parameters:
                page_size: 10
            record_selector:
              extractor:
                field_pointer: ["result"]
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "*ref(definitions.schema_loader)"
            retriever: "*ref(definitions.retriever)"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ValidationError):
            YamlDeclarativeSource(temporary_file.filename)

    def test_source_with_invalid_stream_config_fails_validation(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "*ref(definitions.schema_loader)"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ValidationError):
            YamlDeclarativeSource(temporary_file.filename)


class TestFileContent:
    def __init__(self, content):
        self.file = tempfile.NamedTemporaryFile(mode="w", delete=False)

        with self.file as f:
            f.write(content)

    @property
    def filename(self):
        return self.file.name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.unlink(self.filename)


def test_generate_schema():
    schema_str = YamlDeclarativeSource.generate_schema()
    schema = json.loads(schema_str)

    assert schema["required"] == ["checker", "streams"]
    assert schema["properties"]["checker"]["$ref"] == "#/definitions/CheckStream"
    assert schema["properties"]["streams"]["items"]["$ref"] == "#/definitions/DeclarativeStream"

    check_stream = schema["definitions"]["CheckStream"]
    assert check_stream["required"] == ["stream_names"]
    assert check_stream["properties"]["stream_names"]["type"] == "array"
    assert check_stream["properties"]["stream_names"]["items"]["type"] == "string"

    declarative_stream = schema["definitions"]["DeclarativeStream"]
    assert declarative_stream["required"] == ["schema_loader", "retriever", "config"]
    assert declarative_stream["properties"]["schema_loader"]["$ref"] == "#/definitions/JsonSchema"
    assert declarative_stream["properties"]["retriever"]["$ref"] == "#/definitions/SimpleRetriever"
    assert declarative_stream["properties"]["name"]["type"] == "string"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][0]["type"] == "array"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][0]["items"]["type"] == "string"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][1]["type"] == "array"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][1]["items"]["type"] == "array"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][1]["items"]["items"]["type"] == "string"
    assert declarative_stream["properties"]["primary_key"]["anyOf"][2]["type"] == "string"
    assert declarative_stream["properties"]["stream_cursor_field"]["type"] == "array"
    assert declarative_stream["properties"]["stream_cursor_field"]["items"]["type"] == "string"
    assert declarative_stream["properties"]["transformations"]["type"] == "array"
    assert {"$ref": "#/definitions/AddFields"} in declarative_stream["properties"]["transformations"]["items"]["anyOf"]
    assert {"$ref": "#/definitions/RemoveFields"} in declarative_stream["properties"]["transformations"]["items"]["anyOf"]
    assert declarative_stream["properties"]["checkpoint_interval"]["type"] == "integer"

    simple_retriever = schema["definitions"]["SimpleRetriever"]
    assert simple_retriever["required"] == ["requester", "record_selector"]
    assert simple_retriever["properties"]["requester"]["$ref"] == "#/definitions/HttpRequester"
    assert simple_retriever["properties"]["record_selector"]["$ref"] == "#/definitions/RecordSelector"
    assert simple_retriever["properties"]["name"]["type"] == "string"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][0]["type"] == "array"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][0]["items"]["type"] == "string"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][1]["type"] == "array"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][1]["items"]["type"] == "array"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][1]["items"]["items"]["type"] == "string"
    assert simple_retriever["properties"]["primary_key"]["anyOf"][2]["type"] == "string"
    assert {"$ref": "#/definitions/LimitPaginator"} in simple_retriever["properties"]["paginator"]["anyOf"]
    assert {"$ref": "#/definitions/NoPagination"} in simple_retriever["properties"]["paginator"]["anyOf"]
    assert {"$ref": "#/definitions/CartesianProductStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/DatetimeStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/ListStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/SingleSlice"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/SubstreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]

    http_requester = schema["definitions"]["HttpRequester"]
    assert http_requester["required"] == ["name", "url_base", "path", "config"]
    assert http_requester["properties"]["name"]["type"] == "string"
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]
    assert http_requester["properties"]["http_method"]["anyOf"][0]["type"] == "string"
    assert http_requester["properties"]["http_method"]["anyOf"][1]["type"] == "string"
    assert "GET" in http_requester["properties"]["http_method"]["anyOf"][1]["enum"]
    assert "POST" in http_requester["properties"]["http_method"]["anyOf"][1]["enum"]
    assert http_requester["properties"]["request_options_provider"]["$ref"] == "#/definitions/InterpolatedRequestOptionsProvider"
    assert {"$ref": "#/definitions/DeclarativeOauth2Authenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/ApiKeyAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/BearerAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/BasicHttpAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/CompositeErrorHandler"} in http_requester["properties"]["error_handler"]["anyOf"]
    assert {"$ref": "#/definitions/DefaultErrorHandler"} in http_requester["properties"]["error_handler"]["anyOf"]

    api_key_authenticator = schema["definitions"]["ApiKeyAuthenticator"]
    assert api_key_authenticator["required"] == ["header", "api_token", "config"]
    assert {"$ref": "#/definitions/InterpolatedString"} in api_key_authenticator["properties"]["header"]["anyOf"]
    assert {"type": "string"} in api_key_authenticator["properties"]["header"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in api_key_authenticator["properties"]["api_token"]["anyOf"]
    assert {"type": "string"} in api_key_authenticator["properties"]["api_token"]["anyOf"]

    default_error_handler = schema["definitions"]["DefaultErrorHandler"]
    assert default_error_handler["properties"]["response_filters"]["type"] == "array"
    assert default_error_handler["properties"]["response_filters"]["items"]["$ref"] == "#/definitions/HttpResponseFilter"
    assert default_error_handler["properties"]["max_retries"]["type"] == "integer"
    assert default_error_handler["properties"]["backoff_strategies"]["type"] == "array"
    assert {"$ref": "#/definitions/ConstantBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"]["items"]["anyOf"]
    assert {"$ref": "#/definitions/ExponentialBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"]["items"][
        "anyOf"
    ]
    assert {"$ref": "#/definitions/WaitTimeFromHeaderBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"][
        "items"
    ]["anyOf"]
    assert {"$ref": "#/definitions/WaitUntilTimeFromHeaderBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"][
        "items"
    ]["anyOf"]

    exponential_backoff_strategy = schema["definitions"]["ExponentialBackoffStrategy"]
    assert exponential_backoff_strategy["properties"]["factor"]["type"] == "number"

    limit_paginator = schema["definitions"]["LimitPaginator"]
    assert limit_paginator["required"] == ["page_size", "limit_option", "page_token_option", "pagination_strategy", "config", "url_base"]
    assert limit_paginator["properties"]["page_size"]["type"] == "integer"
    assert limit_paginator["properties"]["limit_option"]["$ref"] == "#/definitions/RequestOption"
    assert limit_paginator["properties"]["page_token_option"]["$ref"] == "#/definitions/RequestOption"
    assert {"$ref": "#/definitions/CursorPaginationStrategy"} in limit_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert {"$ref": "#/definitions/OffsetIncrement"} in limit_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert {"$ref": "#/definitions/PageIncrement"} in limit_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert limit_paginator["properties"]["decoder"]["$ref"] == "#/definitions/JsonDecoder"
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]

    cursor_pagination_stategy = schema["definitions"]["CursorPaginationStrategy"]
    assert cursor_pagination_stategy["required"] == ["cursor_value", "config"]
    assert {"$ref": "#/definitions/InterpolatedString"} in cursor_pagination_stategy["properties"]["cursor_value"]["anyOf"]
    assert {"type": "string"} in cursor_pagination_stategy["properties"]["cursor_value"]["anyOf"]
    assert cursor_pagination_stategy["properties"]["stop_condition"]["$ref"] == "#/definitions/InterpolatedBoolean"
    assert cursor_pagination_stategy["properties"]["decoder"]["$ref"] == "#/definitions/JsonDecoder"

    list_stream_slicer = schema["definitions"]["ListStreamSlicer"]
    assert list_stream_slicer["required"] == ["slice_values", "cursor_field", "config"]
    assert {"type": "array", "items": {"type": "string"}} in list_stream_slicer["properties"]["slice_values"]["anyOf"]
    assert {"type": "string"} in list_stream_slicer["properties"]["slice_values"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in list_stream_slicer["properties"]["cursor_field"]["anyOf"]
    assert {"type": "string"} in list_stream_slicer["properties"]["cursor_field"]["anyOf"]
    assert list_stream_slicer["properties"]["request_option"]["$ref"] == "#/definitions/RequestOption"
