#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import sys
from unittest.mock import patch

import pytest
import yaml
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
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
