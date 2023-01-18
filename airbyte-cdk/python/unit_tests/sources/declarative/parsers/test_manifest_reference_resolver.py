#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.parsers.custom_exceptions import CircularReferenceException, UndefinedReferenceException
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver, _parse_path

resolver = ManifestReferenceResolver()


def test_refer():
    content = {"limit": 50, "limit_ref": "*ref(limit)"}
    config = resolver.preprocess_manifest(content)
    assert config["limit_ref"] == 50


def test_refer_to_inner():
    content = {"dict": {"limit": 50}, "limit_ref": "*ref(dict.limit)"}
    config = resolver.preprocess_manifest(content)
    assert config["limit_ref"] == 50


def test_refer_to_non_existant_struct():
    content = {"dict": {"limit": 50}, "limit_ref": "*ref(not_dict)"}
    with pytest.raises(UndefinedReferenceException):
        resolver.preprocess_manifest(content)


def test_refer_in_dict():
    content = {"limit": 50, "offset_request_parameters": {"offset": "{{ next_page_token['offset'] }}", "limit": "*ref(limit)"}}
    config = resolver.preprocess_manifest(content)
    assert config["offset_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"
    assert config["offset_request_parameters"]["limit"] == 50


def test_refer_to_dict():
    content = {
        "limit": 50,
        "offset_request_parameters": {"offset": "{{ next_page_token['offset'] }}", "limit": "*ref(limit)"},
        "offset_pagination_request_parameters": {
            "class": "InterpolatedRequestParameterProvider",
            "request_parameters": "*ref(offset_request_parameters)",
        },
    }
    config = resolver.preprocess_manifest(content)
    assert config["limit"] == 50
    assert config["offset_request_parameters"]["limit"] == 50
    assert len(config["offset_pagination_request_parameters"]) == 2
    assert config["offset_pagination_request_parameters"]["request_parameters"]["limit"] == 50
    assert config["offset_pagination_request_parameters"]["request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"


def test_refer_and_overwrite():
    content = {
        "limit": 50,
        "custom_limit": 25,
        "offset_request_parameters": {"offset": "{{ next_page_token['offset'] }}", "limit": "*ref(limit)"},
        "custom_request_parameters": {"$ref": "*ref(offset_request_parameters)", "limit": "*ref(custom_limit)"},
    }
    config = resolver.preprocess_manifest(content)
    assert config["offset_request_parameters"]["limit"] == 50
    assert config["custom_request_parameters"]["limit"] == 25

    assert config["offset_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"
    assert config["custom_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"


def test_collision():
    content = {
        "example": {
            "nested": {"path": "first one", "more_nested": {"value": "found it!"}},
            "nested.path": "uh oh",
        },
        "reference_to_nested_path": {"$ref": "*ref(example.nested.path)"},
        "reference_to_nested_nested_value": {"$ref": "*ref(example.nested.more_nested.value)"},
    }
    config = resolver.preprocess_manifest(content)
    assert config["example"]["nested"]["path"] == "first one"
    assert config["example"]["nested.path"] == "uh oh"
    assert config["reference_to_nested_path"] == "uh oh"
    assert config["example"]["nested"]["more_nested"]["value"] == "found it!"
    assert config["reference_to_nested_nested_value"] == "found it!"


def test_internal_collision():
    content = {
        "example": {
            "nested": {"path": {"internal": "uh oh"}, "path.internal": "found it!"},
        },
        "reference": {"$ref": "*ref(example.nested.path.internal)"},
    }
    config = resolver.preprocess_manifest(content)
    assert config["example"]["nested"]["path"]["internal"] == "uh oh"
    assert config["example"]["nested"]["path.internal"] == "found it!"
    assert config["reference"] == "found it!"


def test_parse_path():
    assert _parse_path("foo.bar") == ("foo", "bar")
    assert _parse_path("foo[7][8].bar") == ("foo", "[7][8].bar")
    assert _parse_path("[7][8].bar") == (7, "[8].bar")
    assert _parse_path("[8].bar") == (8, "bar")


def test_list():
    content = {"list": ["A", "B"], "elem_ref": "*ref(list[0])"}
    config = resolver.preprocess_manifest(content)
    elem_ref = config["elem_ref"]
    assert elem_ref == "A"


def test_nested_list():
    content = {"list": [["A"], ["B"]], "elem_ref": "*ref(list[1][0])"}
    config = resolver.preprocess_manifest(content)
    elem_ref = config["elem_ref"]
    assert elem_ref == "B"


def test_list_of_dicts():
    content = {"list": [{"A": "a"}, {"B": "b"}], "elem_ref": "*ref(list[1].B)"}
    config = resolver.preprocess_manifest(content)
    elem_ref = config["elem_ref"]
    assert elem_ref == "b"


def test_multiple_levels_of_indexing():
    content = {"list": [{"A": ["a1", "a2"]}, {"B": ["b1", "b2"]}], "elem_ref": "*ref(list[1].B[0])"}
    config = resolver.preprocess_manifest(content)
    elem_ref = config["elem_ref"]
    assert elem_ref == "b1"


def test_circular_reference():
    content = {"elem_ref1": "*ref(elem_ref2)", "elem_ref2": "*ref(elem_ref1)"}
    with pytest.raises(CircularReferenceException):
        resolver.preprocess_manifest(content)
