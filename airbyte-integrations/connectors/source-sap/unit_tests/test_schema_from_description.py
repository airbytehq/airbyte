"""Schema inference from a DuckDB cursor description.

`connection.execute()` returns the connection, which has no `.types` -- the
types live in `description[i][1]`. Getting this wrong made every ODP OData and
BICS stream silently disappear from `discover`.
"""

import duckdb
import pytest

from source_sap.duck import schema_from_description


@pytest.fixture
def described():
    def _describe(sql):
        return duckdb.connect().execute(sql).description

    return _describe


def test_integer_types(described):
    schema = schema_from_description(described("SELECT 1::INTEGER a, 2::BIGINT b, 3::TINYINT c"))
    for column in ("a", "b", "c"):
        assert schema["properties"][column]["type"] == ["null", "integer"]


def test_floating_and_decimal_types(described):
    schema = schema_from_description(described("SELECT 1.5::DOUBLE a, 1.5::DECIMAL(10,2) b"))
    assert schema["properties"]["a"]["type"] == ["null", "number"]
    assert schema["properties"]["b"]["type"] == ["null", "number"]


def test_temporal_types(described):
    schema = schema_from_description(described("SELECT DATE '2026-01-01' a, TIME '10:00' b, TIMESTAMP '2026-01-01' c"))
    assert schema["properties"]["a"]["format"] == "date"
    assert schema["properties"]["b"]["format"] == "time"
    assert schema["properties"]["c"]["format"] == "date-time"


def test_timestamp_with_time_zone_is_a_date_time(described):
    schema = schema_from_description(described("SELECT now() a"))
    assert schema["properties"]["a"]["format"] == "date-time"


def test_varchar_and_boolean(described):
    schema = schema_from_description(described("SELECT 'x' a, true b"))
    assert schema["properties"]["a"]["type"] == ["null", "string"]
    assert schema["properties"]["b"]["type"] == ["null", "boolean"]


def test_blob_is_base64(described):
    schema = schema_from_description(described("SELECT 'x'::BLOB a"))
    assert schema["properties"]["a"]["contentEncoding"] == "base64"


def test_unknown_type_degrades_to_string(described):
    schema = schema_from_description(described("SELECT [1,2,3] a"))
    assert schema["properties"]["a"]["type"] == ["null", "string"]


def test_shape_is_draft07(described):
    schema = schema_from_description(described("SELECT 1 a"))
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["type"] == "object"


def test_empty_description_is_tolerated():
    assert schema_from_description(None)["properties"] == {}
