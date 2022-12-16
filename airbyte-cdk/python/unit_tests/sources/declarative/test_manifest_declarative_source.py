#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import sys

import pytest
import yaml
from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
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


class TestYamlDeclarativeSource:
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
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        ManifestDeclarativeSource(source_config=manifest)

    def test_manifest_with_spec(self):
        manifest = {
            "version": "version",
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
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
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
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
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
            "not_a_valid_field": "error",
        }
        with pytest.raises(InvalidConnectorDefinitionException):
            ManifestDeclarativeSource(manifest)

    def test_source_missing_checker_fails_validation(self):
        manifest = {
            "version": "version",
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
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
            ManifestDeclarativeSource(manifest)

    def test_source_with_missing_version_fails(self):
        manifest = {
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(manifest)

    def test_source_with_invalid_stream_config_fails_validation(self):
        manifest = {
            "version": "version",
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"}
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        with pytest.raises(ValidationError):
            ManifestDeclarativeSource(manifest)

    def test_source_with_no_external_spec_and_no_in_yaml_spec_fails(self):
        manifest = {
            "version": "version",
            "definitions": {
                "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
                "retriever": {
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                        "page_token_option": {"inject_into": "path"},
                        "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                    },
                    "requester": {
                        "path": "/v3/marketing/lists",
                        "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                        "request_parameters": {"page_size": 10},
                    },
                    "record_selector": {"extractor": {"field_pointer": ["result"]}},
                },
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "$options": {"name": "lists", "primary_key": "id", "url_base": "https://api.sendgrid.com"},
                    "schema_loader": {
                        "name": "{{ options.stream_name }}",
                        "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    },
                    "retriever": {
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size": 10,
                            "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                            "page_token_option": {"inject_into": "path"},
                            "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                        },
                        "requester": {
                            "path": "/v3/marketing/lists",
                            "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                            "request_parameters": {"page_size": 10},
                        },
                        "record_selector": {"extractor": {"field_pointer": ["result"]}},
                    },
                }
            ],
            "check": {"type": "CheckStream", "stream_names": ["lists"]},
        }
        source = ManifestDeclarativeSource(source_config=manifest)

        # We expect to fail here because we have not created a temporary spec.yaml file
        with pytest.raises(FileNotFoundError):
            source.spec(logger)


def test_generate_schema():
    schema_str = ManifestDeclarativeSource.generate_schema()
    schema = json.loads(schema_str)

    assert "version" in schema["required"]
    assert "check" in schema["required"]
    assert "streams" in schema["required"]
    assert schema["properties"]["check"]["$ref"] == "#/definitions/CheckStream"
    assert schema["properties"]["streams"]["items"]["$ref"] == "#/definitions/DeclarativeStream"

    check_stream = schema["definitions"]["CheckStream"]
    assert {"stream_names"}.issubset(check_stream["required"])
    assert check_stream["properties"]["stream_names"]["type"] == "array"
    assert check_stream["properties"]["stream_names"]["items"]["type"] == "string"

    declarative_stream = schema["definitions"]["DeclarativeStream"]
    assert {"retriever", "config"}.issubset(declarative_stream["required"])
    assert {"$ref": "#/definitions/DefaultSchemaLoader"} in declarative_stream["properties"]["schema_loader"]["anyOf"]
    assert {"$ref": "#/definitions/JsonFileSchemaLoader"} in declarative_stream["properties"]["schema_loader"]["anyOf"]
    assert declarative_stream["properties"]["retriever"]["$ref"] == "#/definitions/SimpleRetriever"
    assert declarative_stream["properties"]["name"]["type"] == "string"
    assert {"type": "array", "items": {"type": "string"}} in declarative_stream["properties"]["primary_key"]["anyOf"]
    assert {"type": "array", "items": {"type": "array", "items": {"type": "string"}}} in declarative_stream["properties"]["primary_key"][
        "anyOf"
    ]
    assert {"type": "string"} in declarative_stream["properties"]["primary_key"]["anyOf"]
    assert {"type": "array", "items": {"type": "string"}} in declarative_stream["properties"]["stream_cursor_field"]["anyOf"]
    assert {"type": "string"} in declarative_stream["properties"]["stream_cursor_field"]["anyOf"]
    assert declarative_stream["properties"]["transformations"]["type"] == "array"
    assert {"$ref": "#/definitions/AddFields"} in declarative_stream["properties"]["transformations"]["items"]["anyOf"]
    assert {"$ref": "#/definitions/RemoveFields"} in declarative_stream["properties"]["transformations"]["items"]["anyOf"]
    assert declarative_stream["properties"]["checkpoint_interval"]["type"] == "integer"

    simple_retriever = schema["definitions"]["SimpleRetriever"]["allOf"][1]
    assert {"requester", "record_selector"}.issubset(simple_retriever["required"])
    assert simple_retriever["properties"]["requester"]["$ref"] == "#/definitions/HttpRequester"
    assert simple_retriever["properties"]["record_selector"]["$ref"] == "#/definitions/RecordSelector"
    assert simple_retriever["properties"]["name"]["type"] == "string"
    assert {"type": "array", "items": {"type": "string"}} in declarative_stream["properties"]["primary_key"]["anyOf"]
    assert {"type": "array", "items": {"type": "array", "items": {"type": "string"}}} in declarative_stream["properties"]["primary_key"][
        "anyOf"
    ]
    assert {"type": "string"} in declarative_stream["properties"]["primary_key"]["anyOf"]
    assert {"$ref": "#/definitions/DefaultPaginator"} in simple_retriever["properties"]["paginator"]["anyOf"]
    assert {"$ref": "#/definitions/NoPagination"} in simple_retriever["properties"]["paginator"]["anyOf"]
    assert {"$ref": "#/definitions/CartesianProductStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/DatetimeStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/ListStreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/SingleSlice"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]
    assert {"$ref": "#/definitions/SubstreamSlicer"} in simple_retriever["properties"]["stream_slicer"]["anyOf"]

    http_requester = schema["definitions"]["HttpRequester"]["allOf"][1]
    assert {"name", "url_base", "path", "config"}.issubset(http_requester["required"])
    assert http_requester["properties"]["name"]["type"] == "string"
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["http_method"]["anyOf"]
    assert {"type": "string", "enum": ["GET", "POST"]} in http_requester["properties"]["http_method"]["anyOf"]
    assert http_requester["properties"]["request_options_provider"]["$ref"] == "#/definitions/InterpolatedRequestOptionsProvider"
    assert {"$ref": "#/definitions/DeclarativeOauth2Authenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/ApiKeyAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/BearerAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/BasicHttpAuthenticator"} in http_requester["properties"]["authenticator"]["anyOf"]
    assert {"$ref": "#/definitions/CompositeErrorHandler"} in http_requester["properties"]["error_handler"]["anyOf"]
    assert {"$ref": "#/definitions/DefaultErrorHandler"} in http_requester["properties"]["error_handler"]["anyOf"]

    api_key_authenticator = schema["definitions"]["ApiKeyAuthenticator"]["allOf"][1]
    assert {"header", "api_token", "config"}.issubset(api_key_authenticator["required"])
    assert {"$ref": "#/definitions/InterpolatedString"} in api_key_authenticator["properties"]["header"]["anyOf"]
    assert {"type": "string"} in api_key_authenticator["properties"]["header"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in api_key_authenticator["properties"]["api_token"]["anyOf"]
    assert {"type": "string"} in api_key_authenticator["properties"]["api_token"]["anyOf"]

    default_error_handler = schema["definitions"]["DefaultErrorHandler"]["allOf"][1]
    assert default_error_handler["properties"]["response_filters"]["type"] == "array"
    assert default_error_handler["properties"]["response_filters"]["items"]["$ref"] == "#/definitions/HttpResponseFilter"
    assert default_error_handler["properties"]["max_retries"]["type"] == "integer"
    assert default_error_handler["properties"]["backoff_strategies"]["type"] == "array"

    default_paginator = schema["definitions"]["DefaultPaginator"]["allOf"][1]
    assert {"pagination_strategy", "config", "url_base"}.issubset(default_paginator["required"])
    assert default_paginator["properties"]["page_size_option"]["$ref"] == "#/definitions/RequestOption"
    assert default_paginator["properties"]["page_token_option"]["$ref"] == "#/definitions/RequestOption"
    assert {"$ref": "#/definitions/CursorPaginationStrategy"} in default_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert {"$ref": "#/definitions/OffsetIncrement"} in default_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert {"$ref": "#/definitions/PageIncrement"} in default_paginator["properties"]["pagination_strategy"]["anyOf"]
    assert default_paginator["properties"]["decoder"]["$ref"] == "#/definitions/JsonDecoder"
    assert {"$ref": "#/definitions/InterpolatedString"} in http_requester["properties"]["url_base"]["anyOf"]
    assert {"type": "string"} in http_requester["properties"]["path"]["anyOf"]

    cursor_pagination_strategy = schema["definitions"]["CursorPaginationStrategy"]["allOf"][1]
    assert {"cursor_value", "config"}.issubset(cursor_pagination_strategy["required"])
    assert {"$ref": "#/definitions/InterpolatedString"} in cursor_pagination_strategy["properties"]["cursor_value"]["anyOf"]
    assert {"type": "string"} in cursor_pagination_strategy["properties"]["cursor_value"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedBoolean"} in cursor_pagination_strategy["properties"]["stop_condition"]["anyOf"]
    assert {"type": "string"} in cursor_pagination_strategy["properties"]["stop_condition"]["anyOf"]
    assert cursor_pagination_strategy["properties"]["decoder"]["$ref"] == "#/definitions/JsonDecoder"

    list_stream_slicer = schema["definitions"]["ListStreamSlicer"]["allOf"][1]
    assert {"slice_values", "cursor_field", "config"}.issubset(list_stream_slicer["required"])
    assert {"type": "array", "items": {"type": "string"}} in list_stream_slicer["properties"]["slice_values"]["anyOf"]
    assert {"type": "string"} in list_stream_slicer["properties"]["slice_values"]["anyOf"]
    assert {"$ref": "#/definitions/InterpolatedString"} in list_stream_slicer["properties"]["cursor_field"]["anyOf"]
    assert {"type": "string"} in list_stream_slicer["properties"]["cursor_field"]["anyOf"]
    assert list_stream_slicer["properties"]["request_option"]["$ref"] == "#/definitions/RequestOption"

    added_field_definition = schema["definitions"]["AddedFieldDefinition"]
    assert {"path", "value"}.issubset(added_field_definition["required"])
    assert added_field_definition["properties"]["path"]["type"] == "array"
    assert added_field_definition["properties"]["path"]["items"]["type"] == "string"
    assert {"$ref": "#/definitions/InterpolatedString"} in added_field_definition["properties"]["value"]["anyOf"]
    assert {"type": "string"} in added_field_definition["properties"]["value"]["anyOf"]

    # There is something very strange about JsonSchemaMixin.json_schema(). For some reason, when this test is called independently
    # it will pass. However, when it is invoked with the entire test file, certain components won't get generated in the schema. Since
    # the generate_schema() method is invoked by independently so this doesn't happen under normal circumstance when we generate the
    # complete schema. It only happens when the tests are all called together.
    # One way to replicate this is to add DefaultErrorHandler.json_schema() to the start of this test and uncomment the assertions below

    # assert {"$ref": "#/definitions/ConstantBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"]["items"]["anyOf"]
    # assert {"$ref": "#/definitions/ExponentialBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"]["items"][
    #     "anyOf"
    # ]
    # assert {"$ref": "#/definitions/WaitTimeFromHeaderBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"][
    #     "items"
    # ]["anyOf"]
    # assert {"$ref": "#/definitions/WaitUntilTimeFromHeaderBackoffStrategy"} in default_error_handler["properties"]["backoff_strategies"][
    #     "items"
    # ]["anyOf"]
    #
    # exponential_backoff_strategy = schema["definitions"]["ExponentialBackoffStrategy"]["allOf"][1]
    # assert exponential_backoff_strategy["properties"]["factor"]["type"] == "number"
