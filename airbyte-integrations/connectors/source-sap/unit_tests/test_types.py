"""SAP/DuckDB -> JSON Schema mapping and orjson-safe value coercion."""

import datetime
from decimal import Decimal

import orjson
import pytest

from source_sap.types import coerce_row, json_schema_for_fields, sap_type_to_json_schema


class TestSapTypeToJsonSchema:
    @pytest.mark.parametrize(
        "sap_type,length,decimals,expected",
        [
            ("CHAR", 10, 0, {"type": ["null", "string"]}),
            ("CLNT", 3, 0, {"type": ["null", "string"]}),
            # NUMC keeps leading zeros -> must stay a string
            ("NUMC", 4, 0, {"type": ["null", "string"]}),
            ("ACCP", 6, 0, {"type": ["null", "string"]}),
            ("INT1", 3, 0, {"type": ["null", "integer"]}),
            ("INT4", 10, 0, {"type": ["null", "integer"]}),
            ("INT8", 19, 0, {"type": ["null", "integer"]}),
            ("FLTP", 16, 16, {"type": ["null", "number"]}),
            ("DATS", 8, 0, {"type": ["null", "string"], "format": "date"}),
            ("TIMS", 6, 0, {"type": ["null", "string"], "format": "time"}),
            ("UTCLONG", 27, 0, {"type": ["null", "string"], "format": "date-time"}),
            ("RAW", 16, 0, {"type": ["null", "string"], "contentEncoding": "base64"}),
            ("RAWSTRING", 0, 0, {"type": ["null", "string"], "contentEncoding": "base64"}),
            ("STRING", 0, 0, {"type": ["null", "string"]}),
        ],
    )
    def test_known_types(self, sap_type, length, decimals, expected):
        assert sap_type_to_json_schema(sap_type, length, decimals) == expected

    def test_decimal_types_carry_precision(self):
        # CURR/QUAN/DEC are exact numerics; emitted as JSON number with multipleOf
        got = sap_type_to_json_schema("CURR", 15, 2)
        assert got["type"] == ["null", "number"]
        assert got["airbyte_type"] == "big_number"

    def test_unknown_type_degrades_to_string_and_warns(self, caplog):
        # The old connector raised ValueError here, which broke discover on any
        # table containing an unmapped DDIC type.
        got = sap_type_to_json_schema("WEIRD", 1, 0)
        assert got == {"type": ["null", "string"]}
        assert "WEIRD" in caplog.text

    def test_lowercase_sap_type_is_accepted(self):
        assert sap_type_to_json_schema("char", 1, 0) == {"type": ["null", "string"]}


class TestJsonSchemaForFields:
    def test_builds_draft07_object(self):
        fields = [
            {"technical_name": "CARRID", "abap_type": "CHAR", "length": 3, "decimals": 0, "key": True},
            {"technical_name": "PRICE", "abap_type": "CURR", "length": 15, "decimals": 2, "key": False},
        ]
        schema = json_schema_for_fields(fields)
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert set(schema["properties"]) == {"CARRID", "PRICE"}
        # descriptions must not leak non-standard keys like the old `length`/`decimals`
        assert "length" not in schema["properties"]["CARRID"]

    def test_field_text_becomes_description(self):
        fields = [{"technical_name": "CARRID", "abap_type": "CHAR", "length": 3, "decimals": 0, "text": "Airline"}]
        assert json_schema_for_fields(fields)["properties"]["CARRID"]["description"] == "Airline"


class TestCoerceRow:
    def test_every_value_is_orjson_serializable(self):
        cols = ["D", "T", "TS", "DEC", "B", "S", "N"]
        row = (
            datetime.date(2026, 1, 2),
            datetime.time(3, 4, 5),
            datetime.datetime(2026, 1, 2, 3, 4, 5),
            Decimal("422.94"),
            b"\x00\x01",
            "x",
            None,
        )
        out = coerce_row(cols, row)
        orjson.dumps(out)  # must not raise
        assert out["D"] == "2026-01-02"
        assert out["T"] == "03:04:05"
        assert out["TS"].startswith("2026-01-02T03:04:05")
        assert out["DEC"] == "422.94"
        assert out["B"] == "AAE="  # base64
        assert out["N"] is None

    def test_nested_containers_are_coerced(self):
        out = coerce_row(["L", "M"], ([Decimal("1.5")], {"k": datetime.date(2026, 1, 2)}))
        orjson.dumps(out)
        assert out["L"] == ["1.5"]
        assert out["M"] == {"k": "2026-01-02"}

    def test_plain_values_pass_through_unchanged(self):
        out = coerce_row(["I", "F", "B"], (1, 1.5, True))
        assert out == {"I": 1, "F": 1.5, "B": True}
