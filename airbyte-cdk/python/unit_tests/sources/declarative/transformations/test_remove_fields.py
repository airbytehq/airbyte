#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pytest
from airbyte_cdk.sources.declarative.transformations import RemoveFields
from airbyte_cdk.sources.types import FieldPointer


@pytest.mark.parametrize(
    ["input_record", "field_pointers", "condition", "expected"],
    [
        pytest.param({"k1": "v", "k2": "v"}, [["k1"]], None, {"k2": "v"}, id="remove a field that exists (flat dict), condition = None"),
        pytest.param({"k1": "v", "k2": "v"}, [["k1"]], "", {"k2": "v"}, id="remove a field that exists (flat dict)"),
        pytest.param({"k1": "v", "k2": "v"}, [["k3"]], "", {"k1": "v", "k2": "v"}, id="remove a field that doesn't exist (flat dict)"),
        pytest.param({"k1": "v", "k2": "v"}, [["k1"], ["k2"]], "", {}, id="remove multiple fields that exist (flat dict)"),
        # TODO: should we instead splice the element out of the array? I think that's the more intuitive solution
        #  Otherwise one could just set the field's value to null.
        pytest.param({"k1": [1, 2]}, [["k1", 0]], "", {"k1": [None, 2]}, id="remove field inside array (int index)"),
        pytest.param({"k1": [1, 2]}, [["k1", "0"]], "", {"k1": [None, 2]}, id="remove field inside array (string index)"),
        pytest.param(
            {"k1": "v", "k2": "v", "k3": [0, 1], "k4": "v"},
            [["k1"], ["k2"], ["k3", 0]],
            "",
            {"k3": [None, 1], "k4": "v"},
            id="test all cases (flat)",
        ),
        pytest.param({"k1": [0, 1]}, [[".", "k1", 10]], "", {"k1": [0, 1]}, id="remove array index that doesn't exist (flat)"),
        pytest.param(
            {".": {"k1": [0, 1]}}, [[".", "k1", 10]], "", {".": {"k1": [0, 1]}}, id="remove array index that doesn't exist (nested)"
        ),
        pytest.param({".": {"k2": "v", "k1": "v"}}, [[".", "k1"]], "", {".": {"k2": "v"}}, id="remove nested field that exists"),
        pytest.param(
            {".": {"k2": "v", "k1": "v"}}, [[".", "k3"]], "", {".": {"k2": "v", "k1": "v"}}, id="remove field that doesn't exist (nested)"
        ),
        pytest.param(
            {".": {"k2": "v", "k1": "v"}}, [[".", "k1"], [".", "k2"]], "", {".": {}}, id="remove multiple fields that exist (nested)"
        ),
        pytest.param(
            {".": {"k1": [0, 1]}},
            [[".", "k1", 0]],
            "",
            {".": {"k1": [None, 1]}},
            id="remove multiple fields that exist in arrays (nested)",
        ),
        pytest.param(
            {".": {"k1": [{"k2": "v", "k3": "v"}, {"k4": "v"}]}},
            [[".", "k1", 0, "k2"], [".", "k1", 1, "k4"]],
            "",
            {".": {"k1": [{"k3": "v"}, {}]}},
            id="remove fields that exist in arrays (deeply nested)",
        ),
        pytest.param(
            {"k1": "v", "k2": "v"},
            [["**"]],
            "{{ False }}",
            {"k1": "v", "k2": "v"},
            id="do not remove any field if condition is boolean False",
        ),
        pytest.param({"k1": "v", "k2": "v"}, [["**"]], "{{ True }}", {}, id="remove all field if condition is boolean True"),
        pytest.param(
            {"k1": "v", "k2": "v1", "k3": "v1", "k4": {"k_nested": "v1", "k_nested2": "v2"}},
            [["**"]],
            "{{ property == 'v1' }}",
            {"k1": "v", "k4": {"k_nested2": "v2"}},
            id="recursively remove any field that matches property condition and leave that does not",
        ),
        pytest.param(
            {"k1": "v", "k2": "some_long_string", "k3": "some_long_string", "k4": {"k_nested": "v1", "k_nested2": "v2"}},
            [["**"]],
            "{{ property|length > 5 }}",
            {"k1": "v", "k4": {"k_nested": "v1", "k_nested2": "v2"}},
            id="remove any field that have length > 5 and leave that does not",
        ),
        pytest.param(
            {"k1": 255, "k2": "some_string", "k3": "some_long_string", "k4": {"k_nested": 123123, "k_nested2": "v2"}},
            [["**"]],
            "{{ property is integer }}",
            {"k2": "some_string", "k3": "some_long_string", "k4": {"k_nested2": "v2"}},
            id="recursively remove any field that of type integer and leave that does not",
        ),
    ],
)
def test_remove_fields(input_record: Mapping[str, Any], field_pointers: List[FieldPointer], condition: str, expected: Mapping[str, Any]):
    transformation = RemoveFields(field_pointers=field_pointers, condition=condition, parameters={})
    transformation.transform(input_record)
    assert input_record == expected
