#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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


class MockYamlDeclarativeSource(YamlDeclarativeSource):
    """
    Mock test class that is needed to monkey patch how we read from various files that make up a declarative source because of how our
    tests write configuration files during testing. It is also used to properly namespace where files get written in specific
    cases like when we temporarily write files like spec.yaml to the package unit_tests, which is the directory where it will
    be read in during the tests.
    """

    def _read_and_parse_yaml_file(self, path_to_yaml_file):
        """
        We override the default behavior because we use tempfile to write the yaml manifest to a temporary directory which is
        not mounted during runtime which prevents pkgutil.get_data() from being able to find the yaml file needed to generate
        # the declarative source. For tests we use open() which supports using an absolute path.
        """
        with open(path_to_yaml_file, "r") as f:
            config_content = f.read()
            parsed_config = YamlDeclarativeSource._parse(config_content)
            return parsed_config


class TestYamlDeclarativeSource:
    def test_source_is_created_if_toplevel_fields_are_known(self):
        content = """
        version: "version"
        definitions:
          schema_loader:
            name: "{{ options.stream_name }}"
            file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
          retriever:
            paginator:
              type: "DefaultPaginator"
              page_size: 10
              page_size_option:
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
        MockYamlDeclarativeSource(temporary_file.filename)

    def test_source_fails_for_invalid_yaml(self):
        content = """
        version: "version"
        definitions:
          this is not parsable yaml: " at all
        streams:
          - type: DeclarativeStream
            $options:
              name: "lists"
              primary_key: id
              url_base: "https://api.sendgrid.com"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(ParserError):
            MockYamlDeclarativeSource(temporary_file.filename)

    def test_source_with_missing_reference_fails(self):
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
            retriever: "*ref(definitions.retriever)"
        check:
          type: CheckStream
          stream_names: ["lists"]
        """
        temporary_file = TestFileContent(content)
        with pytest.raises(UndefinedReferenceException):
            MockYamlDeclarativeSource(temporary_file.filename)


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
