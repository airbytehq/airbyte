# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import duckdb
import pyarrow as pa
import pytest
from destination_motherduck.processors.duckdb import _serialize_object_columns


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": ["null", "string"]},
        "count": {"type": ["null", "integer"]},
        "obj": {"type": ["null", "object"]},
        "array_of_objects": {"type": ["null", "array"], "items": {"type": "object"}},
        "array_of_scalars": {"type": ["null", "array"], "items": {"type": "string"}},
    },
}


@pytest.mark.parametrize(
    "col_name, values, expected",
    [
        pytest.param("id", ["a", None], ["a", None], id="scalar_string_untouched"),
        pytest.param("count", [1, None], [1, None], id="scalar_integer_untouched"),
        pytest.param("obj", [{}, {"x": 1}, None], ["{}", '{"x":1}', None], id="object_column_serialized"),
        pytest.param(
            "array_of_objects",
            [[{}], [{"a": 1}], None],
            ["[{}]", '[{"a":1}]', None],
            id="array_of_empty_objects_serialized",
        ),
        pytest.param(
            "array_of_scalars",
            [["a", "b"], [], None],
            ['["a","b"]', "[]", None],
            id="array_of_scalars_serialized",
        ),
        pytest.param("not_in_schema", [{"x": 1}], [{"x": 1}], id="airbyte_column_untouched"),
    ],
)
def test_serialize_object_columns(col_name, values, expected) -> None:
    result = _serialize_object_columns({col_name: values}, JSON_SCHEMA)
    assert result[col_name] == expected


def test_serialize_object_columns_prevents_empty_struct_error() -> None:
    """Regression test for empty STRUCT failure (oncall #13118).

    A `type: array` column whose items are objects, containing an empty object `[{}]`, previously
    reached PyArrow un-serialized and was inferred as `list<struct<>>`, which DuckDB rejects with
    "Attempted to convert a STRUCT with no fields to DuckDB". Serializing it to a JSON string first
    avoids the fieldless struct.
    """
    buffer_data = {"id": ["1"], "array_of_objects": [[{}]]}

    serialized = _serialize_object_columns(buffer_data, JSON_SCHEMA)
    pa_table = pa.Table.from_pydict(serialized)

    # The column must be a string, not a list-of-struct type.
    assert pa.types.is_string(pa_table.schema.field("array_of_objects").type)

    # Registering the table in DuckDB must not raise the empty-struct error.
    con = duckdb.connect()
    con.register("buf", pa_table)
    assert con.execute("SELECT array_of_objects FROM buf").fetchall() == [("[{}]",)]
