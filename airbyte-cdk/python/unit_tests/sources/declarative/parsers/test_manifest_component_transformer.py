#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer


@pytest.mark.parametrize(
    "component, expected_component",
    [
        pytest.param(
            {"type": "DeclarativeSource", "streams": [{"type": "DeclarativeStream", "retriever": {}, "schema_loader": {}}]},
            {
                "type": "DeclarativeSource",
                "streams": [
                    {
                        "type": "DeclarativeStream",
                        "retriever": {"type": "SimpleRetriever"},
                        "schema_loader": {"type": "JsonFileSchemaLoader"},
                    }
                ],
            },
            id="test_declarative_stream",
        ),
        pytest.param(
            {
                "type": "DeclarativeStream",
                "retriever": {"type": "SimpleRetriever", "paginator": {}, "record_selector": {}, "requester": {}},
            },
            {
                "type": "DeclarativeStream",
                "retriever": {
                    "type": "SimpleRetriever",
                    "paginator": {"type": "NoPagination"},
                    "record_selector": {"type": "RecordSelector"},
                    "requester": {"type": "HttpRequester"},
                },
            },
            id="test_simple_retriever",
        ),
        pytest.param(
            {"type": "DeclarativeStream", "requester": {"type": "HttpRequester", "error_handler": {}}},
            {
                "type": "DeclarativeStream",
                "requester": {
                    "type": "HttpRequester",
                    "error_handler": {"type": "DefaultErrorHandler"},
                },
            },
            id="test_http_requester",
        ),
        pytest.param(
            {"type": "SimpleRetriever", "paginator": {"type": "DefaultPaginator", "page_size_option": {}, "page_token_option": {}}},
            {
                "type": "SimpleRetriever",
                "paginator": {
                    "type": "DefaultPaginator",
                    "page_size_option": {"type": "RequestOption"},
                    "page_token_option": {},
                },
            },
            id="test_default_paginator",
        ),
        pytest.param(
            {"type": "SimpleRetriever", "partition_router": {"type": "SubstreamPartitionRouter", "parent_stream_configs": [{}, {}, {}]}},
            {
                "type": "SimpleRetriever",
                "partition_router": {
                    "type": "SubstreamPartitionRouter",
                    "parent_stream_configs": [
                        {"type": "ParentStreamConfig"},
                        {"type": "ParentStreamConfig"},
                        {"type": "ParentStreamConfig"},
                    ],
                },
            },
            id="test_substream_slicer",
        ),
    ],
)
def test_find_default_types(component, expected_component):
    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


@pytest.mark.parametrize(
    "component, expected_component",
    [
        pytest.param(
            {
                "type": "SimpleRetriever",
                "requester": {"type": "HttpRequester", "authenticator": {"class_name": "source_greenhouse.components.NewAuthenticator"}},
            },
            {
                "type": "SimpleRetriever",
                "requester": {
                    "type": "HttpRequester",
                    "authenticator": {"type": "CustomAuthenticator", "class_name": "source_greenhouse.components.NewAuthenticator"},
                },
            },
            id="test_custom_authenticator",
        ),
        pytest.param(
            {
                "type": "SimpleRetriever",
                "record_selector": {
                    "type": "RecordSelector",
                    "extractor": {"class_name": "source_greenhouse.components.NewRecordExtractor"},
                },
            },
            {
                "type": "SimpleRetriever",
                "record_selector": {
                    "type": "RecordSelector",
                    "extractor": {"type": "CustomRecordExtractor", "class_name": "source_greenhouse.components.NewRecordExtractor"},
                },
            },
            id="test_custom_extractor",
        ),
    ],
)
def test_transform_custom_components(component, expected_component):
    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


def test_propagate_parameters_to_all_components():
    component = {
        "type": "DeclarativeSource",
        "streams": [
            {
                "type": "DeclarativeStream",
                "$parameters": {"name": "roasters", "primary_key": "id"},
                "retriever": {
                    "type": "SimpleRetriever",
                    "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": []}},
                    "requester": {
                        "type": "HttpRequester",
                        "name": '{{ parameters["name"] }}',
                        "url_base": "https://coffee.example.io/v1/",
                        "http_method": "GET",
                    },
                },
            }
        ],
    }

    expected_component = {
        "type": "DeclarativeSource",
        "streams": [
            {
                "type": "DeclarativeStream",
                "retriever": {
                    "type": "SimpleRetriever",
                    "name": "roasters",
                    "primary_key": "id",
                    "record_selector": {
                        "type": "RecordSelector",
                        "extractor": {
                            "type": "DpathExtractor",
                            "field_path": [],
                            "name": "roasters",
                            "primary_key": "id",
                            "$parameters": {"name": "roasters", "primary_key": "id"},
                        },
                        "name": "roasters",
                        "primary_key": "id",
                        "$parameters": {"name": "roasters", "primary_key": "id"},
                    },
                    "requester": {
                        "type": "HttpRequester",
                        "name": '{{ parameters["name"] }}',
                        "url_base": "https://coffee.example.io/v1/",
                        "http_method": "GET",
                        "primary_key": "id",
                        "$parameters": {"name": "roasters", "primary_key": "id"},
                    },
                    "$parameters": {"name": "roasters", "primary_key": "id"},
                },
                "name": "roasters",
                "primary_key": "id",
                "$parameters": {"name": "roasters", "primary_key": "id"},
            }
        ],
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


def test_component_parameters_take_precedence_over_parent_parameters():
    component = {
        "type": "DeclarativeStream",
        "retriever": {
            "type": "SimpleRetriever",
            "requester": {
                "type": "HttpRequester",
                "name": "high_priority",
                "url_base": "https://coffee.example.io/v1/",
                "http_method": "GET",
                "primary_key": "id",
                "$parameters": {
                    "name": "high_priority",
                },
            },
            "$parameters": {
                "name": "low_priority",
            },
        },
    }

    expected_component = {
        "type": "DeclarativeStream",
        "retriever": {
            "type": "SimpleRetriever",
            "name": "low_priority",
            "requester": {
                "type": "HttpRequester",
                "name": "high_priority",
                "url_base": "https://coffee.example.io/v1/",
                "http_method": "GET",
                "primary_key": "id",
                "$parameters": {
                    "name": "high_priority",
                },
            },
            "$parameters": {
                "name": "low_priority",
            },
        },
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


def test_do_not_propagate_parameters_that_have_the_same_field_name():
    component = {
        "type": "DeclarativeStream",
        "streams": [
            {
                "type": "DeclarativeStream",
                "$parameters": {
                    "name": "roasters",
                    "primary_key": "id",
                    "schema_loader": {"type": "JsonFileSchemaLoader", "file_path": './source_coffee/schemas/{{ parameters["name"] }}.json'},
                },
            }
        ],
    }

    expected_component = {
        "type": "DeclarativeStream",
        "streams": [
            {
                "type": "DeclarativeStream",
                "name": "roasters",
                "primary_key": "id",
                "schema_loader": {
                    "type": "JsonFileSchemaLoader",
                    "file_path": './source_coffee/schemas/{{ parameters["name"] }}.json',
                    "name": "roasters",
                    "primary_key": "id",
                    "$parameters": {
                        "name": "roasters",
                        "primary_key": "id",
                    },
                },
                "$parameters": {
                    "name": "roasters",
                    "primary_key": "id",
                    "schema_loader": {"type": "JsonFileSchemaLoader", "file_path": './source_coffee/schemas/{{ parameters["name"] }}.json'},
                },
            }
        ],
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


def test_ignore_empty_parameters():
    component = {
        "type": "DeclarativeStream",
        "retriever": {
            "type": "SimpleRetriever",
            "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": []}},
        },
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == component


def test_only_propagate_parameters_to_components():
    component = {
        "type": "ParentComponent",
        "component_with_object_properties": {
            "type": "TestComponent",
            "subcomponent": {
                "type": "TestSubComponent",
                "some_field": "high_priority",
                "$parameters": {
                    "some_option": "already",
                },
            },
            "dictionary_field": {"details": "should_not_contain_parameters", "other": "no_parameters_as_fields"},
            "$parameters": {
                "included": "not!",
            },
        },
    }

    expected_component = {
        "type": "ParentComponent",
        "component_with_object_properties": {
            "type": "TestComponent",
            "subcomponent": {
                "type": "TestSubComponent",
                "some_field": "high_priority",
                "some_option": "already",
                "included": "not!",
                "$parameters": {"some_option": "already", "included": "not!"},
            },
            "dictionary_field": {"details": "should_not_contain_parameters", "other": "no_parameters_as_fields"},
            "included": "not!",
            "$parameters": {
                "included": "not!",
            },
        },
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component


def test_do_not_propagate_parameters_on_json_schema_object():
    component = {
        "type": "DeclarativeStream",
        "streams": [
            {
                "type": "DeclarativeStream",
                "schema_loader": {
                    "type": "InlineSchemaLoader",
                    "schema": {
                        "type": "object",
                        "$schema": "http://json-schema.org/schema#",
                        "properties": {"id": {"type": "string"}},
                    },
                },
                "$parameters": {
                    "name": "roasters",
                    "primary_key": "id",
                },
            }
        ],
    }

    expected_component = {
        "type": "DeclarativeStream",
        "streams": [
            {
                "type": "DeclarativeStream",
                "name": "roasters",
                "primary_key": "id",
                "schema_loader": {
                    "type": "InlineSchemaLoader",
                    "name": "roasters",
                    "primary_key": "id",
                    "schema": {
                        "type": "object",
                        "$schema": "http://json-schema.org/schema#",
                        "properties": {"id": {"type": "string"}},
                    },
                    "$parameters": {
                        "name": "roasters",
                        "primary_key": "id",
                    },
                },
                "$parameters": {
                    "name": "roasters",
                    "primary_key": "id",
                },
            }
        ],
    }

    transformer = ManifestComponentTransformer()
    actual_component = transformer.propagate_types_and_parameters("", component, {})

    assert actual_component == expected_component
