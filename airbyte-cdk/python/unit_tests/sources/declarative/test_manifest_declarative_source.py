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
            "version": "version",
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
            "version": "version",
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
            "version": "version",
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
            "version": "version",
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
            "version": "version",
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
        manifest = {"version": "version", "definitions": None, "check": {"type": "CheckStream", "stream_names": ["lists"]}}
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

    def test_source_with_invalid_stream_config_fails_validation(self):
        manifest = {
            "version": "version",
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
            "version": "version",
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
            "version": "version",
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
            "version": "version",
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
