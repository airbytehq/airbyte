#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import tempfile

import pytest
from airbyte_cdk.sources.declarative.parsers.custom_exceptions import UndefinedReferenceException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from yaml.parser import ParserError

logger = logging.getLogger("airbyte")


EXTERNAL_CONNECTION_SPECIFICATION = {
    "type": "object",
    "required": ["api_token"],
    "additionalProperties": False,
    "properties": {"api_token": {"type": "string"}},
}


class TestYamlDeclarativeSource:
    def test_source_is_created_if_toplevel_fields_are_known(self):
        content = """
        version: "0.29.3"
        definitions:
          schema_loader:
            name: "{{ parameters.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ parameters.name }}.yaml"
          retriever:
            paginator:
              type: "DefaultPaginator"
              page_size: 10
              page_size_option:
                inject_into: request_parameter
                field_name: page_size
              page_token_option:
                type: RequestPath
              pagination_strategy:
                type: "CursorPagination"
                cursor_value: "{{ response._metadata.next }}"
            requester:
              url_base: "https://api.sendgrid.com"
              path: "/v3/marketing/lists"
              authenticator:
                type: "BearerAuthenticator"
                api_token: "{{ config.apikey }}"
              request_parameters:
                page_size: "{{ 10 }}"
            record_selector:
              extractor:
                field_path: ["result"]
        streams:
          - type: DeclarativeStream
            $parameters:
              name: "lists"
              primary_key: id
            schema_loader: "#/definitions/schema_loader"
            retriever: "#/definitions/retriever"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        YamlDeclarativeSource(temporary_file.filename)

    def test_source_fails_for_invalid_yaml(self):
        content = """
        version: "version"
        definitions:
          this is not parsable yaml: " at all
        streams:
          - type: DeclarativeStream
            $parameters:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ParserError):
            YamlDeclarativeSource(temporary_file.filename)

    def test_source_with_missing_reference_fails(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ parameters.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ parameters.name }}.yaml"
        streams:
          - type: DeclarativeStream
            $parameters:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
            schema_loader: "#/definitions/schema_loader"
            retriever: "#/definitions/retriever"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(UndefinedReferenceException):
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
