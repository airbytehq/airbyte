#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

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
