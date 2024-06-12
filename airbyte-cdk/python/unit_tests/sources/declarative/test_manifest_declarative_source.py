#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import sys
from copy import deepcopy
from typing import Any, List, Mapping
from unittest.mock import call, patch

import pytest
import requests
import yaml
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Level,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from jsonschema.exceptions import ValidationError

logger = logging.getLogger("airbyte")

EXTERNAL_CONNECTION_SPECIFICATION = {
    "type": "object",
    "required": ["api_token"],
    "additionalProperties": False,
    "properties": {"api_token": {"type": "string"}},
}


class MockManifestDeclarativeSource(ManifestDeclarativeSource):
    """
    Mock test class that is needed to monkey patch how we read from various files that make up a declarative source because of how our
    tests write configuration files during testing. It is also used to properly namespace where files get written in specific
    cases like when we temporarily write files like spec.yaml to the package unit_tests, which is the directory where it will
    be read in during the tests.
    """


class TestManifestDeclarativeSource:
    @pytest.fixture
    def use_external_yaml_spec(self):
        # Our way of resolving the absolute path to root of the airbyte-cdk unit test directory where spec.yaml files should
        # be written to (i.e. ~/airbyte/airbyte-cdk/python/unit-tests) because that is where they are read from during testing.
        module = sys.modules[__name__]
        module_path = os.path.abspath(module.__file__)
        test_path = os.path.dirname(module_path)
        spec_root = test_path.split("/sources/declarative")[0]

        spec = {"documentationUrl": "https://airbyte.com/#yaml-from-external", "connectionSpecification": EXTERNAL_CONNECTION_SPECIFICATION}

        yaml_path = os.path.join(spec_root, "spec.yaml")
        with open(yaml_path, "w") as f:
            f.write(yaml.dump(spec))
        yield
        os.remove(yaml_path)

    def test_valid_manifest(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {},
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "stream_with_custom_requester", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "type": "CustomRequester",
                            "class_name": "unit_tests.sources.declarative.external_component.SampleCustomComponent",
                            "path": "/v3/marketing/lists",
                            "custom_request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        source = ManifestDeclarativeSource(source_config=manifest)

        check_stream = source.connection_checker
        check_stream.check_connection(source, logging.getLogger(""), {})

        streams = source.streams({})
        assert len(streams) == 2
        assert isinstance(streams[0], DeclarativeStream)
        assert isinstance(streams[1], DeclarativeStream)

    def test_manifest_with_spec(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": "{{ 10 }}"},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
            "spec": {
                "type": "Spec",
                "documentation_url": "https://airbyte.com/#yaml-from-manifest",
                "connection_specification": {
                    "title": "Test Spec",
                    "type": "object",
                    "required": ["api_key"],
                    "additionalProperties": False,
                    "properties": {
                        "api_key": {"type": "string", "airbyte_secret": True, "title": "API Key", "description": "Test API Key", "order": 0}
                    },
                },
            },
        }
        source = ManifestDeclarativeSource(source_config=manifest)
        connector_specification = source.spec(logger)
        assert connector_specification is not None
        assert connector_specification.documentationUrl == "https://airbyte.com/#yaml-from-manifest"
        assert connector_specification.connectionSpecification["title"] == "Test Spec"
        assert connector_specification.connectionSpecification["required"][0] == "api_key"
        assert connector_specification.connectionSpecification["additionalProperties"] is False
        assert connector_specification.connectionSpecification["properties"]["api_key"] == {
            "type": "string",
            "airbyte_secret": True,
            "title": "API Key",
            "description": "Test API Key",
            "order": 0,
        }

    def test_manifest_with_external_spec(self, use_external_yaml_spec):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": "{{ 10 }}"},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        source = MockManifestDeclarativeSource(source_config=manifest)

        connector_specification = source.spec(logger)

        assert connector_specification.documentationUrl == "https://airbyte.com/#yaml-from-external"
        assert connector_specification.connectionSpecification == EXTERNAL_CONNECTION_SPECIFICATION

    def test_source_is_not_created_if_toplevel_fields_are_unknown(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
            "not_a_valid_field": "error",
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    def test_source_missing_checker_fails_validation(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream"},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    def test_source_with_missing_streams_fails(self):
        manifest = {"version": "0.29.3", "definitions": None, "check": {"type": "CheckStream", "stream_names": ["lists"]}}
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    def test_source_with_missing_version_fails(self):
        manifest = {
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    @pytest.mark.parametrize(
        "cdk_version, manifest_version, expected_error",
        [
            pytest.param("0.35.0", "0.30.0", None, id="manifest_version_less_than_cdk_package_should_run"),
            pytest.param("1.5.0", "0.29.0", None, id="manifest_version_less_than_cdk_major_package_should_run"),
            pytest.param("0.29.0", "0.29.0", None, id="manifest_version_matching_cdk_package_should_run"),
            pytest.param(
                "0.29.0",
                "0.25.0",
                ValidationError,
                id="manifest_version_before_beta_that_uses_the_beta_0.29.0_cdk_package_should_throw_error",
            ),
            pytest.param(
                "1.5.0",
                "0.25.0",
                ValidationError,
                id="manifest_version_before_beta_that_uses_package_later_major_version_than_beta_0.29.0_cdk_package_should_throw_error",
            ),
            pytest.param("0.34.0", "0.35.0", ValidationError, id="manifest_version_greater_than_cdk_package_should_throw_error"),
            pytest.param("0.29.0", "-1.5.0", ValidationError, id="manifest_version_has_invalid_major_format"),
            pytest.param("0.29.0", "0.invalid.0", ValidationError, id="manifest_version_has_invalid_minor_format"),
            pytest.param("0.29.0", "0.29.0.1", ValidationError, id="manifest_version_has_extra_version_parts"),
            pytest.param("0.29.0", "5.0", ValidationError, id="manifest_version_has_too_few_version_parts"),
            pytest.param("0.29.0:dev", "0.29.0", ValidationError, id="manifest_version_has_extra_release"),
        ],
    )
    @patch("importlib.metadata.version")
    def test_manifest_versions(self, version, cdk_version, manifest_version, expected_error):
        # Used to mock the metadata.version() for test scenarios which normally returns the actual version of the airbyte-cdk package
        version.return_value = cdk_version

        manifest = {
            "version": manifest_version,
            "definitions": {},
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "stream_with_custom_requester", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "type": "CustomRequester",
                            "class_name": "unit_tests.sources.declarative.external_component.SampleCustomComponent",
                            "path": "/v3/marketing/lists",
                            "custom_request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        if expected_error:
            with pytest.raises(expected_error):
                ManifestDeclarativeSource(source_config=manifest)
        else:
            ManifestDeclarativeSource(source_config=manifest)

    def test_source_with_invalid_stream_config_fails_validation(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                }
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    def test_source_with_no_external_spec_and_no_in_yaml_spec_fails(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": "{{ 10 }}"},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        source = ManifestDeclarativeSource(source_config=manifest)

        # We expect to fail here because we have not created a temporary spec.yaml file
        with pytest.raises(FileNotFoundError):
            source.spec(logger)

    def test_manifest_without_at_least_one_stream(self):
        manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_path": ["result"]}},
                },
            },
            "streams": [],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(source_config=manifest)

    @patch("airbyte_cdk.sources.declarative.declarative_source.DeclarativeSource.read")
    def test_given_debug_when_read_then_set_log_level(self, declarative_source_read):
        any_valid_manifest = {
            "version": "0.29.3",
            "definitions": {
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"type": "RequestPath"},
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
                    "$parameters": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": "{{ 10 }}"},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
                {
                    "type": "DeclarativeStream",
                    "$parameters": {"name": "stream_with_custom_requester", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ parameters.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"type": "RequestPath"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "cursor_value": "{{ response._metadata.next }}",
                                "page_size": 10,
                            },
                        },
                        "requester": {
                            "type": "CustomRequester",
                            "class_name": "unit_tests.sources.declarative.external_component.SampleCustomComponent",
                            "path": "/v3/marketing/lists",
                            "custom_request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_path": ["result"]}},
                    },
                },
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        source = ManifestDeclarativeSource(source_config=any_valid_manifest, debug=True)

        debug_logger = logging.getLogger("logger.debug")
        list(source.read(debug_logger, {}, {}, {}))

        assert debug_logger.isEnabledFor(logging.DEBUG)


def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def _create_request():
    url = "https://example.com/api"
    headers = {"Content-Type": "application/json"}
    return requests.Request("POST", url, headers=headers, json={"key": "value"}).prepare()


def _create_response(body):
    response = requests.Response()
    response.status_code = 200
    response._content = bytes(json.dumps(body), "utf-8")
    response.headers["Content-Type"] = "application/json"
    return response


def _create_page(response_body):
    response = _create_response(response_body)
    response.request = _create_request()
    return response


@pytest.mark.parametrize(
    "test_name, manifest, pages, expected_records, expected_calls",
    [
        (
            "test_read_manifest_no_pagination_no_partitions",
            {
                "version": "0.34.2",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["Rates"]},
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "name": "Rates",
                        "primary_key": [],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "ABC": {"type": "number"},
                                    "AED": {"type": "number"},
                                },
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.apilayer.com",
                                "path": "/exchangerates_data/latest",
                                "http_method": "GET",
                                "request_parameters": {},
                                "request_headers": {},
                                "request_body_json": {},
                                "authenticator": {
                                    "type": "ApiKeyAuthenticator",
                                    "header": "apikey",
                                    "api_token": "{{ config['api_key'] }}",
                                },
                            },
                            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["rates"]}},
                            "paginator": {"type": "NoPagination"},
                        },
                    }
                ],
                "spec": {
                    "connection_specification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "required": ["api_key"],
                        "properties": {"api_key": {"type": "string", "title": "API Key", "airbyte_secret": True}},
                        "additionalProperties": True,
                    },
                    "documentation_url": "https://example.org",
                    "type": "Spec",
                },
            },
            (
                _create_page({"rates": [{"ABC": 0}, {"AED": 1}], "_metadata": {"next": "next"}}),
                _create_page({"rates": [{"USD": 2}], "_metadata": {"next": "next"}}),
            )
            * 10,
            [{"ABC": 0}, {"AED": 1}],
            [call({}, {})],
        ),
        (
            "test_read_manifest_with_added_fields",
            {
                "version": "0.34.2",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["Rates"]},
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "name": "Rates",
                        "primary_key": [],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "ABC": {"type": "number"},
                                    "AED": {"type": "number"},
                                },
                                "type": "object",
                            },
                        },
                        "transformations": [
                            {
                                "type": "AddFields",
                                "fields": [{"type": "AddedFieldDefinition", "path": ["added_field_key"], "value": "added_field_value"}],
                            }
                        ],
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.apilayer.com",
                                "path": "/exchangerates_data/latest",
                                "http_method": "GET",
                                "request_parameters": {},
                                "request_headers": {},
                                "request_body_json": {},
                                "authenticator": {
                                    "type": "ApiKeyAuthenticator",
                                    "header": "apikey",
                                    "api_token": "{{ config['api_key'] }}",
                                },
                            },
                            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["rates"]}},
                            "paginator": {"type": "NoPagination"},
                        },
                    }
                ],
                "spec": {
                    "connection_specification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "required": ["api_key"],
                        "properties": {"api_key": {"type": "string", "title": "API Key", "airbyte_secret": True}},
                        "additionalProperties": True,
                    },
                    "documentation_url": "https://example.org",
                    "type": "Spec",
                },
            },
            (
                _create_page({"rates": [{"ABC": 0}, {"AED": 1}], "_metadata": {"next": "next"}}),
                _create_page({"rates": [{"USD": 2}], "_metadata": {"next": "next"}}),
            )
            * 10,
            [{"ABC": 0, "added_field_key": "added_field_value"}, {"AED": 1, "added_field_key": "added_field_value"}],
            [call({}, {})],
        ),
        (
            "test_read_with_pagination_no_partitions",
            {
                "version": "0.34.2",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["Rates"]},
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "name": "Rates",
                        "primary_key": [],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "ABC": {"type": "number"},
                                    "AED": {"type": "number"},
                                    "USD": {"type": "number"},
                                },
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.apilayer.com",
                                "path": "/exchangerates_data/latest",
                                "http_method": "GET",
                                "request_parameters": {},
                                "request_headers": {},
                                "request_body_json": {},
                                "authenticator": {
                                    "type": "ApiKeyAuthenticator",
                                    "header": "apikey",
                                    "api_token": "{{ config['api_key'] }}",
                                },
                            },
                            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["rates"]}},
                            "paginator": {
                                "type": "DefaultPaginator",
                                "page_size": 2,
                                "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                                "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                                "pagination_strategy": {
                                    "type": "CursorPagination",
                                    "cursor_value": "{{ response._metadata.next }}",
                                    "page_size": 2,
                                },
                            },
                        },
                    }
                ],
                "spec": {
                    "connection_specification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "required": ["api_key"],
                        "properties": {"api_key": {"type": "string", "title": "API Key", "airbyte_secret": True}},
                        "additionalProperties": True,
                    },
                    "documentation_url": "https://example.org",
                    "type": "Spec",
                },
            },
            (
                _create_page({"rates": [{"ABC": 0}, {"AED": 1}], "_metadata": {"next": "next"}}),
                _create_page({"rates": [{"USD": 2}], "_metadata": {}}),
            )
            * 10,
            [{"ABC": 0}, {"AED": 1}, {"USD": 2}],
            [call({}, {}), call({"next_page_token": "next"}, {"next_page_token": "next"})],
        ),
        (
            "test_no_pagination_with_partition_router",
            {
                "version": "0.34.2",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["Rates"]},
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "name": "Rates",
                        "primary_key": [],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {"ABC": {"type": "number"}, "AED": {"type": "number"}, "partition": {"type": "number"}},
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.apilayer.com",
                                "path": "/exchangerates_data/latest",
                                "http_method": "GET",
                                "request_parameters": {},
                                "request_headers": {},
                                "request_body_json": {},
                                "authenticator": {
                                    "type": "ApiKeyAuthenticator",
                                    "header": "apikey",
                                    "api_token": "{{ config['api_key'] }}",
                                },
                            },
                            "partition_router": {"type": "ListPartitionRouter", "values": ["0", "1"], "cursor_field": "partition"},
                            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["rates"]}},
                            "paginator": {"type": "NoPagination"},
                        },
                    }
                ],
                "spec": {
                    "connection_specification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "required": ["api_key"],
                        "properties": {"api_key": {"type": "string", "title": "API Key", "airbyte_secret": True}},
                        "additionalProperties": True,
                    },
                    "documentation_url": "https://example.org",
                    "type": "Spec",
                },
            },
            (
                _create_page({"rates": [{"ABC": 0, "partition": 0}, {"AED": 1, "partition": 0}], "_metadata": {"next": "next"}}),
                _create_page({"rates": [{"ABC": 2, "partition": 1}], "_metadata": {"next": "next"}}),
            ),
            [{"ABC": 0, "partition": 0}, {"AED": 1, "partition": 0}, {"ABC": 2, "partition": 1}],
            [call({}, {"partition": "0"}, None), call({}, {"partition": "1"}, None)],
        ),
        (
            "test_with_pagination_and_partition_router",
            {
                "version": "0.34.2",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["Rates"]},
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "name": "Rates",
                        "primary_key": [],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {"ABC": {"type": "number"}, "AED": {"type": "number"}, "partition": {"type": "number"}},
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.apilayer.com",
                                "path": "/exchangerates_data/latest",
                                "http_method": "GET",
                                "request_parameters": {},
                                "request_headers": {},
                                "request_body_json": {},
                                "authenticator": {
                                    "type": "ApiKeyAuthenticator",
                                    "header": "apikey",
                                    "api_token": "{{ config['api_key'] }}",
                                },
                            },
                            "partition_router": {"type": "ListPartitionRouter", "values": ["0", "1"], "cursor_field": "partition"},
                            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["rates"]}},
                            "paginator": {
                                "type": "DefaultPaginator",
                                "page_size": 2,
                                "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                                "page_token_option": {"inject_into": "path", "type": "RequestPath"},
                                "pagination_strategy": {
                                    "type": "CursorPagination",
                                    "cursor_value": "{{ response._metadata.next }}",
                                    "page_size": 2,
                                },
                            },
                        },
                    }
                ],
                "spec": {
                    "connection_specification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "required": ["api_key"],
                        "properties": {"api_key": {"type": "string", "title": "API Key", "airbyte_secret": True}},
                        "additionalProperties": True,
                    },
                    "documentation_url": "https://example.org",
                    "type": "Spec",
                },
            },
            (
                _create_page({"rates": [{"ABC": 0, "partition": 0}, {"AED": 1, "partition": 0}], "_metadata": {"next": "next"}}),
                _create_page({"rates": [{"USD": 3, "partition": 0}], "_metadata": {}}),
                _create_page({"rates": [{"ABC": 2, "partition": 1}], "_metadata": {}}),
            ),
            [{"ABC": 0, "partition": 0}, {"AED": 1, "partition": 0}, {"USD": 3, "partition": 0}, {"ABC": 2, "partition": 1}],
            [
                call({}, {"partition": "0"}, None),
                call({}, {"partition": "0"}, {"next_page_token": "next"}),
                call({}, {"partition": "1"}, None),
            ],
        ),
    ],
)
def test_read_manifest_declarative_source(test_name, manifest, pages, expected_records, expected_calls):
    _stream_name = "Rates"
    with patch.object(SimpleRetriever, "_fetch_next_page", side_effect=pages) as mock_retriever:
        output_data = [message.record.data for message in _run_read(manifest, _stream_name) if message.record]
        assert output_data == expected_records
        mock_retriever.assert_has_calls(expected_calls)


def test_only_parent_streams_use_cache():
    applications_stream = {
        "type": "DeclarativeStream",
        "$parameters": {"name": "applications", "primary_key": "id", "url_base": "https://harvest.greenhouse.io/v1/"},
        "schema_loader": {
            "name": "{{ parameters.stream_name }}",
            "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
        },
        "retriever": {
            "paginator": {
                "type": "DefaultPaginator",
                "page_size": 10,
                "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "per_page"},
                "page_token_option": {"type": "RequestPath"},
                "pagination_strategy": {
                    "type": "CursorPagination",
                    "cursor_value": "{{ headers['link']['next']['url'] }}",
                    "stop_condition": "{{ 'next' not in headers['link'] }}",
                    "page_size": 100,
                },
            },
            "requester": {
                "path": "applications",
                "authenticator": {"type": "BasicHttpAuthenticator", "username": "{{ config['api_key'] }}"},
            },
            "record_selector": {"extractor": {"type": "DpathExtractor", "field_path": []}},
        },
    }

    manifest = {
        "version": "0.29.3",
        "definitions": {},
        "streams": [
            deepcopy(applications_stream),
            {
                "type": "DeclarativeStream",
                "$parameters": {"name": "applications_interviews", "primary_key": "id", "url_base": "https://harvest.greenhouse.io/v1/"},
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "per_page"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {
                            "type": "CursorPagination",
                            "cursor_value": "{{ headers['link']['next']['url'] }}",
                            "stop_condition": "{{ 'next' not in headers['link'] }}",
                            "page_size": 100,
                        },
                    },
                    "requester": {
                        "path": "applications_interviews",
                        "authenticator": {"type": "BasicHttpAuthenticator", "username": "{{ config['api_key'] }}"},
                    },
                    "record_selector": {"extractor": {"type": "DpathExtractor", "field_path": []}},
                    "partition_router": {
                        "parent_stream_configs": [
                            {"parent_key": "id", "partition_field": "parent_id", "stream": deepcopy(applications_stream)}
                        ],
                        "type": "SubstreamPartitionRouter",
                    },
                },
            },
            {
                "type": "DeclarativeStream",
                "$parameters": {"name": "jobs", "primary_key": "id", "url_base": "https://harvest.greenhouse.io/v1/"},
                "schema_loader": {
                    "name": "{{ parameters.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ parameters.name }}.yaml",
                },
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "per_page"},
                        "page_token_option": {"type": "RequestPath"},
                        "pagination_strategy": {
                            "type": "CursorPagination",
                            "cursor_value": "{{ headers['link']['next']['url'] }}",
                            "stop_condition": "{{ 'next' not in headers['link'] }}",
                            "page_size": 100,
                        },
                    },
                    "requester": {
                        "path": "jobs",
                        "authenticator": {"type": "BasicHttpAuthenticator", "username": "{{ config['api_key'] }}"},
                    },
                    "record_selector": {"extractor": {"type": "DpathExtractor", "field_path": []}},
                },
            },
        ],
        "check": {"type": "CheckStream", "stream_names": ["applications"]},
    }
    source = ManifestDeclarativeSource(source_config=manifest)

    streams = source.streams({})
    assert len(streams) == 3

    # Main stream with caching (parent for substream `applications_interviews`)
    assert streams[0].name == "applications"
    assert streams[0].retriever.requester.use_cache

    # Substream
    assert streams[1].name == "applications_interviews"
    assert not streams[1].retriever.requester.use_cache

    # Parent stream created for substream
    assert streams[1].retriever.stream_slicer.parent_stream_configs[0].stream.name == "applications"
    assert streams[1].retriever.stream_slicer.parent_stream_configs[0].stream.retriever.requester.use_cache

    # Main stream without caching
    assert streams[2].name == "jobs"
    assert not streams[2].retriever.requester.use_cache


def _run_read(manifest: Mapping[str, Any], stream_name: str) -> List[AirbyteMessage]:
    source = ManifestDeclarativeSource(source_config=manifest)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )
    return list(source.read(logger, {}, catalog, {}))
