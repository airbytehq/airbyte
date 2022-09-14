#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pytest
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import FieldPointer


@pytest.mark.parametrize(
    ["input_record", "field", "kwargs", "expected"],
    [
        pytest.param({"k": "v"}, [(["path"], "static_value")], {}, {"k": "v", "path": "static_value"}, id="add new static value"),
        pytest.param(
            {"k": "v"},
            [(["path"], "static_value"), (["path2"], "static_value2")],
            {},
            {"k": "v", "path": "static_value", "path2": "static_value2"},
            id="add new multiple static values",
        ),
        pytest.param(
            {"k": "v"},
            [(["nested", "path"], "static_value")],
            {},
            {"k": "v", "nested": {"path": "static_value"}},
            id="set static value at nested path",
        ),
        pytest.param({"k": "v"}, [(["k"], "new_value")], {}, {"k": "new_value"}, id="update value which already exists"),
        pytest.param({"k": [0, 1]}, [(["k", 3], "v")], {}, {"k": [0, 1, None, "v"]}, id="Set element inside array"),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ config["shop"] }}')],
            {"config": {"shop": "in-n-out"}},
            {"k": "v", "k2": "in-n-out"},
            id="set a value from the config using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ config.shop }}")],
            {"config": {"shop": "in-n-out"}},
            {"k": "v", "k2": "in-n-out"},
            id="set a value from the config using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ stream_state["cursor"] }}')],
            {"stream_state": {"cursor": "t0"}},
            {"k": "v", "k2": "t0"},
            id="set a value from the state using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ stream_state.cursor }}")],
            {"stream_state": {"cursor": "t0"}},
            {"k": "v", "k2": "t0"},
            id="set a value from the state using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ stream_slice["start_date"] }}')],
            {"stream_slice": {"start_date": "oct1"}},
            {"k": "v", "k2": "oct1"},
            id="set a value from the stream slice using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ stream_slice.start_date }}")],
            {"stream_slice": {"start_date": "oct1"}},
            {"k": "v", "k2": "oct1"},
            id="set a value from the stream slice using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ record.k }}")],
            {},
            {"k": "v", "k2": "v"},
            id="set a value from a field in the record using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ record["k"] }}')],
            {},
            {"k": "v", "k2": "v"},
            id="set a value from a field in the record using bracket notation",
        ),
        pytest.param(
            {"k": {"nested": "v"}},
            [(["k2"], "{{ record.k.nested }}")],
            {},
            {"k": {"nested": "v"}, "k2": "v"},
            id="set a value from a nested field in the record using bracket notation",
        ),
        pytest.param(
            {"k": {"nested": "v"}},
            [(["k2"], '{{ record["k"]["nested"] }}')],
            {},
            {"k": {"nested": "v"}, "k2": "v"},
            id="set a value from a nested field in the record using bracket notation",
        ),
        pytest.param({"k": "v"}, [(["k2"], "{{ 2 + 2 }}")], {}, {"k": "v", "k2": 4}, id="set a value from a jinja expression"),
    ],
)
def test_add_fields(
    input_record: Mapping[str, Any], field: List[Tuple[FieldPointer, str]], kwargs: Mapping[str, Any], expected: Mapping[str, Any]
):
    inputs = [AddedFieldDefinition(path=v[0], value=v[1], options={}) for v in field]
    assert AddFields(fields=inputs, options={"alas": "i live"}).transform(input_record, **kwargs) == expected
