#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple

import pytest
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.types import FieldPointer


@pytest.mark.parametrize(
    ["input_record", "field", "field_type", "kwargs", "expected"],
    [
        pytest.param({"k": "v"}, [(["path"], "static_value")], None, {}, {"k": "v", "path": "static_value"}, id="add new static value"),
        pytest.param({"k": "v"}, [(["path"], "{{ 1 }}")], None, {}, {"k": "v", "path": 1}, id="add an expression evaluated as a number"),
        pytest.param(
            {"k": "v"},
            [(["path"], "{{ 1 }}")],
            str,
            {},
            {"k": "v", "path": "1"},
            id="add an expression evaluated as a string using the value_type field",
        ),
        pytest.param(
            {"k": "v"},
            [(["path"], "static_value"), (["path2"], "static_value2")],
            None,
            {},
            {"k": "v", "path": "static_value", "path2": "static_value2"},
            id="add new multiple static values",
        ),
        pytest.param(
            {"k": "v"},
            [(["nested", "path"], "static_value")],
            None,
            {},
            {"k": "v", "nested": {"path": "static_value"}},
            id="set static value at nested path",
        ),
        pytest.param({"k": "v"}, [(["k"], "new_value")], None, {}, {"k": "new_value"}, id="update value which already exists"),
        pytest.param({"k": [0, 1]}, [(["k", 3], "v")], None, {}, {"k": [0, 1, None, "v"]}, id="Set element inside array"),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ config["shop"] }}')],
            None,
            {"config": {"shop": "in-n-out"}},
            {"k": "v", "k2": "in-n-out"},
            id="set a value from the config using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ config.shop }}")],
            None,
            {"config": {"shop": "in-n-out"}},
            {"k": "v", "k2": "in-n-out"},
            id="set a value from the config using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ stream_state["cursor"] }}')],
            None,
            {"stream_state": {"cursor": "t0"}},
            {"k": "v", "k2": "t0"},
            id="set a value from the state using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ stream_state.cursor }}")],
            None,
            {"stream_state": {"cursor": "t0"}},
            {"k": "v", "k2": "t0"},
            id="set a value from the state using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ stream_slice["start_date"] }}')],
            None,
            {"stream_slice": {"start_date": "oct1"}},
            {"k": "v", "k2": "oct1"},
            id="set a value from the stream slice using bracket notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ stream_slice.start_date }}")],
            None,
            {"stream_slice": {"start_date": "oct1"}},
            {"k": "v", "k2": "oct1"},
            id="set a value from the stream slice using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], "{{ record.k }}")],
            None,
            {},
            {"k": "v", "k2": "v"},
            id="set a value from a field in the record using dot notation",
        ),
        pytest.param(
            {"k": "v"},
            [(["k2"], '{{ record["k"] }}')],
            None,
            {},
            {"k": "v", "k2": "v"},
            id="set a value from a field in the record using bracket notation",
        ),
        pytest.param(
            {"k": {"nested": "v"}},
            [(["k2"], "{{ record.k.nested }}")],
            None,
            {},
            {"k": {"nested": "v"}, "k2": "v"},
            id="set a value from a nested field in the record using bracket notation",
        ),
        pytest.param(
            {"k": {"nested": "v"}},
            [(["k2"], '{{ record["k"]["nested"] }}')],
            None,
            {},
            {"k": {"nested": "v"}, "k2": "v"},
            id="set a value from a nested field in the record using bracket notation",
        ),
        pytest.param({"k": "v"}, [(["k2"], "{{ 2 + 2 }}")], None, {}, {"k": "v", "k2": 4}, id="set a value from a jinja expression"),
    ],
)
def test_add_fields(
    input_record: Mapping[str, Any],
    field: List[Tuple[FieldPointer, str]],
    field_type: Optional[str],
    kwargs: Mapping[str, Any],
    expected: Mapping[str, Any],
):
    inputs = [AddedFieldDefinition(path=v[0], value=v[1], value_type=field_type, parameters={}) for v in field]
    assert AddFields(fields=inputs, parameters={"alas": "i live"}).transform(input_record, **kwargs) == expected
